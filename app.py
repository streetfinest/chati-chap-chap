from flask import Flask, request, jsonify, send_from_directory
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

messages = []

HTML = """
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chati Chap Chap Pro</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 15px; background-color: #ece5dd; }
        .msg { background: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: relative; }
        
        /* Hii inaruhusu maandishi kuweza kuselectiwa kwa kidole kwenye simu */
        .msg-text { 
            font-size: 16px; 
            margin-top: 15px; 
            user-select: text; 
            -webkit-user-select: text; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            color: #333;
        }
        
        .msg img { max-width: 100%; border-radius: 5px; margin-top: 10px; cursor: pointer; }
        
        /* Muonekano wa Copy Button */
        .copy-btn { 
            font-size: 12px; cursor: pointer; color: white; background: #075E54; 
            border: none; padding: 5px 10px; border-radius: 4px; 
            position: absolute; top: 10px; right: 10px; transition: 0.3s;
        }
        
        #chat-box { height: 65vh; overflow-y: auto; margin-bottom: 15px; }
        form { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
        input[type="text"], input[type="file"] { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button[type="submit"] { width: 100%; padding: 15px; background: #128C7E; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
        
        /* Zoom Modal */
        .modal { display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; }
        .modal img { max-width: 90%; max-height: 90%; border-radius: 5px; }
    </style>
</head>
<body>
    <h2 style="text-align: center; color: #075E54;">Chati Chap Chap 🚀</h2>
    <div id="chat-box"></div>
    
    <form id="uploadForm" onsubmit="tumaUjumbe(event)">
        <input type="file" id="file" name="file">
        <input type="text" id="text" name="text" placeholder="Andika ujumbe (au tuma picha tu)...">
        <button type="submit" id="btnTuma">TUMA</button>
    </form>

    <!-- Modal kwa ajili ya zoom -->
    <div id="imageModal" class="modal" onclick="this.style.display='none'">
        <img id="modalImg" src="">
    </div>

    <script>
        // Mbinu mbadala inayofanya kazi kwenye simu (hata kama sio HTTPS)
        function kopiMaandishi(btn) {
            // Chukua maandishi husika chini ya button hii
            let textDiv = btn.parentElement.querySelector('.msg-text');
            let text = textDiv.innerText;

            // Tengeneza ki-box kilichofichwa kwa ajili ya kulazimisha Copy kwenye simu
            let textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";  // Kuzuia page kushuka chini
            textArea.style.top = "0";
            textArea.style.left = "0";
            textArea.style.opacity = "0";       // Kuficha isionekane
            document.body.appendChild(textArea);
            
            textArea.focus();
            textArea.select();

            try {
                // Hii ndio command inayo-force simu na PC kufanya "Copy"
                document.execCommand('copy');
                
                // Badilisha button iwe ya kijani na kuandika 'Imekopiwa!'
                let oldText = btn.innerText;
                btn.innerText = "Imekopiwa! ✔";
                btn.style.background = "#25D366";
                
                // Irudishe kwenye hali ya kawaida baada ya sekunde 2
                setTimeout(() => {
                    btn.innerText = oldText;
                    btn.style.background = "#075E54";
                }, 2000);
            } catch (err) {
                alert("Kukopi kumegoma, jaribu kuselect mwenyewe.");
            }
            
            document.body.removeChild(textArea); // Futa ki-box kilichofichwa
        }

        function zoomImage(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('imageModal').style.display = 'flex';
        }

        function vutaMessages() {
            fetch('/messages').then(res => res.json()).then(data => {
                let box = document.getElementById('chat-box');
                box.innerHTML = '';
                data.forEach(msg => {
                    let div = document.createElement('div');
                    div.className = 'msg';
                    let content = '';
                    
                    if(msg.text) {
                        content += `<button class="copy-btn" onclick="kopiMaandishi(this)">Copy</button>`;
                        content += `<div class="msg-text">${msg.text}</div>`;
                    }
                    
                    if(msg.file) {
                        if(msg.file.match(/\\.(jpeg|jpg|gif|png|webp)$/i)) {
                            content += `<img src="/uploads/${msg.file}" onclick="zoomImage('/uploads/${msg.file}')">`;
                        } else {
                            content += `<br><a href="/uploads/${msg.file}" target="_blank">📄 Fungua Faili: ${msg.file}</a>`;
                        }
                    }
                    div.innerHTML = content;
                    box.appendChild(div);
                });
            });
        }
        setInterval(vutaMessages, 2000);
        vutaMessages();

        function tumaUjumbe(e) {
            e.preventDefault();
            let text = document.getElementById('text').value;
            let file = document.getElementById('file').files[0];
            
            if (!text && !file) return alert("Tafadhali weka maandishi au chagua faili kwanza!");

            let btn = document.getElementById('btnTuma');
            btn.innerText = "Inatuma...";
            
            let fd = new FormData(document.getElementById('uploadForm'));
            fetch('/upload', { method: 'POST', body: fd }).then(() => {
                document.getElementById('uploadForm').reset();
                btn.innerText = "TUMA";
                vutaMessages();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return HTML

@app.route('/upload', methods=['POST'])
def upload():
    text = request.form.get('text', '')
    file = request.files.get('file')
    filename = None
    if file and file.filename:
        filename = str(int(time.time())) + "_" + file.filename.replace(" ", "_")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    messages.insert(0, {'text': text, 'file': filename})
    return jsonify({"status": "success"})

@app.route('/messages')
def get_messages(): return jsonify(messages)

@app.route('/uploads/<filename>')
def get_file(filename): return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)