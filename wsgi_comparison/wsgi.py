from bottle import Bottle, static_file, request

app = Bottle()

@app.route("/")
def hello():
    return static_file("index.html", '.')

@app.route("/htmx.js")
def htmx():
    return static_file("htmx.js", '.')

@app.route("/fun", method="GET")
def fun_template():
    return """<textarea placeholder="Type some nonsense then tab / click away!" 
        hx-post="/fun" hx-target="#fun-outputs" hx-swap="innerHTML" 
        name="fun-input" id="fun-input" cols="60" rows="20"></textarea>
        <div id="fun-outputs"></div>"""


@app.route("/fun", method="POST")
def fun_handler():
    fun_input = request.forms.get("fun-input", "")
    if len(fun_input):
        return f"""
            <h1>{len(fun_input)} Characters Processed! REVERSE REVERSE!</h1>
            <div>{fun_input[::-1]}</div>"""


app.run(host="localhost", port=8080, debug=True, reloader=True)
