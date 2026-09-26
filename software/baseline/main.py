from flask import Flask, jsonify, request, render_template
import asyncio
from core.task_manager import TaskTicketManager
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_model import Response
import logging
from flask_cors import CORS
from ask_sdk_model import LaunchRequest, IntentRequest, SessionEndedRequest
import json

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
task_manager = TaskTicketManager()

# Create or get event loop
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

class GetNewTaskIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.debug(f"Checking GetNewTaskIntentHandler: {type(handler_input.request_envelope.request)}")
        return (isinstance(handler_input.request_envelope.request, IntentRequest) and
                handler_input.request_envelope.request.intent.name == "GetNewTaskIntent")
    
    def handle(self, handler_input):
        logger.debug("Handling get new task intent")
        
        try:
            task = loop.run_until_complete(
                task_manager.selector.get_next_task(task_manager.trello, task_manager.history)
            )
            
            if task:
                task_manager.current_task = task
                task_manager.print_task_ticket(task)
                task_manager.history.add_task(task)
                speech_text = "Ho stampato un nuovo compito per te. Fammi sapere quando lo completi."
                reprompt = "Hai completato il compito?"
            else:
                speech_text = "Non sono riuscito a trovare un compito adatto in questo momento. Riprova più tardi."
                reprompt = "Vuoi provare a cercare un altro compito?"
            
            return handler_input.response_builder\
                .speak(speech_text)\
                .ask(reprompt)\
                .set_should_end_session(False)\
                .response
                
        except Exception as e:
            logger.error(f"Error in GetNewTaskIntentHandler: {str(e)}", exc_info=True)
            speech_text = "Mi dispiace, c'è stato un errore durante la stampa del compito. Riprova più tardi."
            return handler_input.response_builder\
                .speak(speech_text)\
                .set_should_end_session(True)\
                .response

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.debug(f"Checking YesIntentHandler: {type(handler_input.request_envelope.request)}")
        return (isinstance(handler_input.request_envelope.request, IntentRequest) and
                handler_input.request_envelope.request.intent.name == "AMAZON.YesIntent")
    
    def handle(self, handler_input):
        logger.debug("Handling yes intent")
        try:
            if task_manager.current_task:
                if task_manager.current_task['source_list'] in ['TODO', 'DOING']:
                    success = loop.run_until_complete(
                        task_manager.move_task_to_done(
                            task_manager.current_task['task_id'], 
                            task_manager.current_task['source_list']
                        )
                    )
                    if success:
                        task_manager.history.mark_completed(task_manager.current_task['task_id'])
                        speech_text = "Ottimo! Ho segnato il compito come completato."
                    else:
                        speech_text = "Ho avuto problemi a segnare il compito come completato. Riprova."
                else:
                    speech_text = "Questo compito non ha bisogno di essere segnato come completato."
            else:
                speech_text = "Non c'è nessun compito attivo da completare. Vuoi un nuovo compito?"
            
            reprompt = "Vuoi un altro compito?"
            return handler_input.response_builder\
                .speak(speech_text)\
                .ask(reprompt)\
                .set_should_end_session(False)\
                .response
                
        except Exception as e:
            logger.error(f"Error in YesIntentHandler: {str(e)}", exc_info=True)
            speech_text = "Mi dispiace, c'è stato un errore. Riprova più tardi."
            return handler_input.response_builder\
                .speak(speech_text)\
                .set_should_end_session(True)\
                .response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.debug(f"Checking NoIntentHandler: {type(handler_input.request_envelope.request)}")
        return (isinstance(handler_input.request_envelope.request, IntentRequest) and
                handler_input.request_envelope.request.intent.name == "AMAZON.NoIntent")
    
    def handle(self, handler_input):
        logger.debug("Handling no intent")
        try:
            if task_manager.current_task:
                logger.debug(f"Marking task as skipped: {task_manager.current_task['task_id']}")
                task_manager.history.add_skipped_task(task_manager.current_task['task_id'])
                logger.debug("Task marked as skipped")
                speech_text = "Ok, ho segnato questo compito come saltato. Provane un altro quando vuoi!"
            else:
                speech_text = "Ok, nessun problema! Fammi sapere quando vuoi un compito."
        except Exception as e:
            logger.error(f"Error in NoIntentHandler: {e}", exc_info=True)
            speech_text = "Ok, nessun problema! Fammi sapere quando vuoi un altro compito."
            
        return handler_input.response_builder\
            .speak(speech_text)\
            .set_should_end_session(True)\
            .response

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return isinstance(handler_input.request_envelope.request, LaunchRequest)

    def handle(self, handler_input):
        logger.debug("Handling launch request")
        
        # Get task immediately instead of asking
        task = loop.run_until_complete(
            task_manager.selector.get_next_task(task_manager.trello, task_manager.history)
        )
        
        if task:
            task_manager.current_task = task
            task_manager.print_task_ticket(task)
            task_manager.history.add_task(task)
            speech_text = "Ho stampato un nuovo compito per te. Fammi sapere quando lo completi."
        else:
            speech_text = "Non sono riuscito a trovare un compito adatto in questo momento. Riprova più tardi."
            
        return handler_input.response_builder.speak(speech_text).ask("Hai completato il compito?").response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        logger.debug(f"Checking SessionEndedRequestHandler: {type(handler_input.request_envelope.request)}")
        return isinstance(handler_input.request_envelope.request, SessionEndedRequest)

    def handle(self, handler_input):
        logger.debug("Handling session ended request")
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        logger.error(f"Exception occurred: {exception}", exc_info=True)
        return True

    def handle(self, handler_input, exception):
        logger.error(f"Error handling request: {exception}", exc_info=True)
        speech = "Sorry, I had trouble processing that request. Please try again."
        return handler_input.response_builder.speak(speech).ask(speech).response

# Create skill builder
sb = SkillBuilder()

# Add request handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetNewTaskIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Add exception handler
sb.add_exception_handler(CatchAllExceptionHandler())

# Create skill adapter
skill_adapter = SkillAdapter(
    skill=sb.create(),
    skill_id="amzn1.ask.skill.400e264f-3982-44ff-9ee5-625d8fd1209e",
    app=app
)

@app.route("/", methods=['POST', 'GET', 'OPTIONS'])
@app.route("/alexa", methods=['POST', 'GET', 'OPTIONS'])
def invoke_skill():
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.debug("Received request to Alexa endpoint")
    try:
        return skill_adapter.dispatch_request()
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return str(e), 500

@app.route("/print_task", methods=['POST'])
def print_task():
    try:
        task = loop.run_until_complete(
            task_manager.selector.get_next_task(task_manager.trello, task_manager.history)
        )
        
        if task:
            task_manager.current_task = task
            task_manager.print_task_ticket(task)
            task_manager.history.add_task(task)
            return jsonify({
                "success": True,
                "message": "Task printed successfully",
                "task": task
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No suitable task found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error printing task: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500
        
@app.route("/display", methods=['GET'])
def display():
    return render_template('display.html')

@app.route("/complete_task", methods=['POST'])
def complete_task():
    try:
        data = request.json
        task_id = data.get('task_id')
        source_list = data.get('source_list')
        
        if not task_id or not source_list:
            return jsonify({
                "success": False,
                "message": "Missing task_id or source_list"
            }), 400
            
        success = loop.run_until_complete(
            task_manager.move_task_to_done(task_id, source_list)
        )
        
        if success:
            task_manager.history.mark_completed(task_id)
            # Reset current task
            task_manager.current_task = None
            return jsonify({
                "success": True,
                "message": "Task marked as completed"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to move task to DONE list"
            }), 500
            
    except Exception as e:
        logger.error(f"Error completing task: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route("/skip_task", methods=['POST'])
def skip_task():
    try:
        data = request.json
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({
                "success": False,
                "message": "Missing task_id"
            }), 400
            
        task_manager.history.add_skipped_task(task_id)
        # Reset current task
        task_manager.current_task = None
        
        return jsonify({
            "success": True,
            "message": "Task marked as skipped"
        }), 200
            
    except Exception as e:
        logger.error(f"Error skipping task: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)