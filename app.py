from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import openai
import datetime
import re
from easygoogletranslate import EasyGoogleTranslate

app = Flask(__name__)

limiter = Limiter(key_func=get_remote_address,auto_check=False)
limiter.init_app(app)

openai.api_key = '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'

def translate_text(source_language, target_language, text_to_translate):
    translator = EasyGoogleTranslate(
        source_language=source_language,
        target_language=target_language,
        timeout=10
    )
    result = translator.translate(text_to_translate)

    return result

def gpt_response(user_text, print_output=False):
    
    completions = openai.Completion.create(
        engine='text-davinci-003',     # Determines the quality, speed, and cost.
        temperature=0.9,            # Level of creativity in the response
        prompt=f"Engage in a conversation with AI assistant Alapchari, framing responses in the context of Bangladesh and Bengali culture. Responses must contain simple sentence structures, common vocabulary, and straightforward grammar. Alapchari does not comment on political events or figures. \nUser: {user_text}\nAlapcari: ",
        max_tokens=220,             # Maximum tokens in the prompt AND response
        n=1,                        # The number of completions to generate
        stop=None,                  # An optional setting to control response generation
    )


    
    response_json = json.dumps(completions.to_dict())
    response_dict = json.loads(response_json)
    generated_text = response_dict["choices"][0]["text"]

    # Displaying the output can be helpful if things go wrong
    #if print_output:
    #   print(generated_text)
    # Return the first choice's text
    return generated_text



def write_to_file(prompt, response):
    current_time = datetime.datetime.now().strftime("%I:%M %p, %d-%m-%Y")
    # output = {"prompt": prompt, "response": response, "translated_prompt": en_prompt, "en_response": en_response, "time": current_time}

    output = {
        "prompt": prompt,
        "response": response,
        "time": current_time
    }
    output_json = json.dumps(output, ensure_ascii=False)
    
    # Set an initial count value for the function
    with open("chat_data.txt", "a", encoding='utf-8') as file:
        file.write(output_json + "\n")


def write_prompt(prompt):
    with open('prompts.txt', 'a', encoding='utf-8') as f:
        f.write(f'{{"{prompt}"}},\n')



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cross_origin()
def serve(path):
    return render_template('index.html')


@app.route('/chatrik', methods=['POST'])
@limiter.limit('10 per minute')
@cross_origin()
def chinference():

    if not limiter.check():
        if request.method == 'POST':
            # Get the JSON input from the request
            json_data = request.get_json()

            # Check if the 'prompt' key exists in the JSON input
            if 'prompt' not in json_data:
                return jsonify({'error': 'No prompt found in JSON input'}), 400

            # Call the 'inference' function with the 'prompt' value
            prompt = json_data['prompt']
            # Writes the prompt to prompt.txt
            write_prompt(prompt)

            # Using google translate
            ## result, en_prompt, en_response = inference(prompt)
            ## write_to_file(prompt, result, en_prompt, en_response)

            result = chat_inference(prompt)
            
            write_to_file(prompt, result)
            # Return a JSON response with the result
            return jsonify({'result': result})
    else:
        return jsonify({'error': 'too many requests'})






def break_sentence(sentence):
    words = re.findall(r'\b[ঀ-৾]{2,}(?!\w)', sentence, re.UNICODE)
    return words

def translate_pair(source_language, target_language, text):
    translator = EasyGoogleTranslate(
        source_language=source_language,
        target_language=target_language,
        timeout=100
    )
    bn_array = break_sentence(text)
    
    en_array = eval(translator.translate(str(bn_array)))

    rstr = ''
    for word, translation in zip(bn_array, en_array):
            rstr += f'{word} - {translation}\n'

    return rstr


#def inference(prompt):
    # This is the function that does the actual inference based on the 'prompt' value
    translated_prompt = translate_text('bn','en', prompt)
    gpt_reply = gpt_response(translated_prompt)
    result = translate_text('en', 'bn', gpt_reply)

    response = result
    return response, translated_prompt, gpt_reply



def chat_inference(prompt):
    #translation = 'some text\nsometext\nsome text'
    translation = translate_pair('bn', 'en', prompt)
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[
            {"role": "system", "content": f"Your name is Alapchari(আলাপচারী), a curious and friendly ai assistant made by Fahmidul Hasan, a student at United International University. Users can talk to you bengali using unicode or latin letters but you only respond in bengali."},
            {"role": "user", "content": str(prompt) + " For better understanding of the users prompt here are the direct translation of each word the user is saying:\n{translation}"},
        ],
    temperature=0.3
    )
    print("Prompt:" + f"Your name is Alapchari(আলাপচারী), a curious and friendly ai assistant made by Fahmidul Hasan, a student at United International University. Users can talk to you bengali using unicode or latin letters but you only respond in bengali. For better understanding of the users prompt here are the direct translation of each word the user is saying:\n{translation}")
    print(completion)
    return completion["choices"][0]["message"]["content"]


if __name__ == '__main__':
    app.run(debug=False)



