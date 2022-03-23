[View it on my blog](https://tech.gerardbentley.com/streamlit/python/beginner/2022/03/23/bottle-htmx-streamlit.html)

Local setup (assumes working [python installation](https://tech.gerardbentley.com/python/beginner/2022/01/29/install-python.html)):

```sh
git clone git@github.com:gerardrbentley/streamlit-random.git
cd streamlit-random/wsgi_comparison
# Start the bottle server
python wsgi.py 
# in another terminal start streamlit
pip install streamlit
streamlit run streamlit_app.py
```

# Bottle + HTMX vs Streamlit

**NOTE:** This isn't a debate that real people have.

So why compare them...?

It's a comparison of workflows for quickly building small, interactive web apps.

`streamlit` is the new hotness in Data Science and Machine Learning.
It basically turns Python scripts into websites, pre-styled and pre-packaged with a good looking component library.
But its install size is not small!

The Python web framework `bottle` and the Javascript/HTML power tool `htmx` are each dependency free and each is contained in a single `.py` / `.js` file (js can be loaded from cdn).

`bottle` is [~4500 lines of Python](https://github.com/bottlepy/bottle/blob/master/bottle.py) and `htmx` is [~3000 lines of Javascript (unminified)](https://github.com/bigskysoftware/htmx/blob/master/src/htmx.js).
Combining the two allows for writing interactive apps with just Python and HTML.

But first some context for people who haven't heard of `bottle` and `htmx`.

## Python Full Stack Development

Before I found `streamlit` I played with different Python web frameworks (`flask`, `klein`, `twisted`, `django`, etc.).
They all try to make spinning up a web server *easier* (some with a heavier hand than others *cough* django *cough*).

They all have some templating mechanism (ex. `jinja2`) for sending html to the frontend.
But many modern "full-stack" tutorials won't bother with this feature.

The flavor of the moment I've seen is **JSON Rest Api** + **React/Vue/Angular Frontend**.
So as an aspiring developer I've hacked away at Vue projects (like a [timer app](https://repeter.gerardbentley.com/) for daily tasks) to figure out web-workers and browser storage work.
And I've gone through courses such as [Django Channels + Angular + Docker](https://testdriven.io/courses/real-time-app-with-django-channels-and-angular/) to learn wtf a websocket is.
I even did some minor work on a `react` + `express` admin app for a startup.

But I have never been able to get invested in the javascript ecosystem & accept the size of `node_modules`.
(Saying this fully aware of Python's packaging woes...)

## A Simpler Web Stack

If you've run code like `django-admin startproject mysite` then fired up a webserver without understanding the magic of the background that is totally fine.

To get a grip on *why* `django` does what it does, you can spend some time with `bottle`.

A simple bottle app that returns `hello world` on a GET request might look like the following:

```py
from bottle import route, run

@route('/')
def index():
    return 'hello world'

run(host='localhost', port=8080)
```

Running this code in a normal Python script (i.e. `python my_bottle_app.py`) will run a server on your local machine.
Going to a browser with url <http://localhost:8080/> should show you 'hello world'.
You can also use a program like `curl` (or Python `requests`) to fetch the data as an API request.

**HOLD UP**

WTF is a `route` or a `localhost` or a `port`?

## An Easier Web Stack

Let's compare this to a `streamlit` hello world.

```py
import streamlit as st
st.write('hello world')
```

To run this we need to use `streamlit run my_streamlit_app.py` (you may need `python -m streamlit run ...` to specify the current Python interpreter)

Then we should automagically get a browser window open with our 'hello world' displayed, styled, and part of a larger app with a hamburger menu that can change the theme and do some other things.

One major drawback is we don't get access to our code via API (see this [github issue](https://github.com/streamlit/streamlit/issues/439#issuecomment-1075970927) for my hack on adding API routes to your Streamlit app's `tornado` server).

## Bottle + HTMX

To actually get cooking with gas, let's demo an interactive `bottle` webpage.
If you don't want to see raw HTML, avert your attention now.

```py
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
```

If you have played around with `flask`, this app creation pattern and adding routes with decorators might be a little familiar.

Returning HTML strings with random `hx-` element attributes is probably not familiar at all.

### Static Files

To be explicit, I've included 2 routes to serve the 2 necessary static files.
Bottle does have the ability to serve static files from a directory on a wildcard route.

`index.html` holds the skeleton of the app.
Just including the interesting bits here:

```html
<head>
    <script src="htmx.js"></script>
</head>

<body>
    <button hx-get="/fun" 
            hx-target="#app" 
            hx-swap="innerHTML">🎉 Do Something Fun!</button>
    <div id="app"></div>
</body>
```

At the top we have a standard `<script>` tag to load in the file at `/htmx.js`, which is the raw `htmx` library (included as raw file for showcase, serve it gzipped / from cdn in production).

The `htmx` magic comes in the `hx-get`, `hx-target` and `hx-swap` attributes.

When the `button` is clicked, it will make a GET request to `/fun`.
It then takes the response from `/fun` and injects it into the `innerHTML` of the `#app` element (the `div` in this case).

All powered by `htmx` using 3 HTML attributes!

### Get Routes in Bottle + HTMX

Next we have a route that handles GET requests to `/fun`.

On the `bottle` side of things we just want to return the HTML template for the "fun zone" (tm 🎉).
Which with syntax highlighting looks like:

```html
<textarea placeholder="Type some nonsense then tab / click away!" 
    hx-post="/fun" hx-target="#fun-outputs" hx-swap="innerHTML" 
    name="fun-input" id="fun-input" cols="60" rows="20"></textarea>
<div id="fun-outputs"></div>
```

The first element returned is a `textarea` for inputting random text.
When the content of this `textarea` changes, a POST request will be sent to `/fun` (note the `hx-post="/fun"`), and the response will be injected into the `innerHTML` of the `fun-outputs` `div`.

### Post Routes in Bottle + HTMX

`htmx` can send data from our html widgets in a post request (see the docs for more understanding of [request triggers](https://htmx.org/docs/#triggers) such as with HTML forms).

`bottle` can then parse this request data and do something with it!

```py
fun_input = request.forms.get("fun-input", "")
```

In this case, we'll return the message in reverse and announce how long the string is.
By returning HTML, it will get displayed nicely in the element specified by `hx-target`.

In the case where there isn't any actual text, it will implicitly return None and won't update the display.

```py
if len(fun_input):
    return f"""
        <h1>{len(fun_input)} Characters Processed! REVERSE REVERSE!</h1>
        <div>{fun_input[::-1]}</div>"""
```

*NOTE* this doesn't use built in `bottle` templating for simplicity.

Admittedly, `bottle` uses a similarly confusing global request object to `flask`, but "Pay no attention to that man behind the curtain!"

## Doing it with Streamlit

Already the `bottle` example has grown in complexity and "things to know about".

So far the concepts outside of Python (that all require coding attention!) are:

- HTML
- Ports / Hostnames
- Server / wsgi loops
- URL routes
- HTTP request methods
- How `htmx` works

And if we wanted to deploy this to the world we'd also want to know (and spend time on):

- CSS styling
- Static file deployment / bundling
- Gunicorn / Gevent / production wsgi serving
- Testing interaction between HTML and routes

What if we could shove all of that mountain of stuff onto the shoulders of `streamlit`...?

*NOTE* These are all awesome things to learn!
[The Odin Project](https://www.theodinproject.com/) is an awesome resource and community for learning the **web** parts that Python learners usually don't come into web apps with.

Porting the example to streamlit, we can reduce it from 2 files (`index.html` and `wsgi.py`) to 1 (`streamlit_app.py`) and can reduce the lines of code we need to understand from ~50 to ~15.

```py
import streamlit as st

if st.button("Do Something Fun 🎉!"):
    st.session_state['show_fun'] = True
elif 'show_fun' not in st.session_state:
    st.session_state['show_fun'] = False

if st.session_state.show_fun:
    fun_input = st.text_area('', placeholder='Type some nonsense then hit cmd/ctrl + enter')
    if len(fun_input):
        st.header(f"{len(fun_input)} Characters Processed! REVERSE REVERSE!")
        st.write(fun_input[::-1])
```

No more HTML... Replaced with:

- `st.button`
- `st.text_area`
- `st.header`
- `st.write`

No more Ports / server / routes... Replaced with:

`streamlit run streamlit_app.py`

No more HTTP requests or `htmx`... Replaced with:

- `if st.button("Do Something Fun 🎉!"):`
- `fun_input = st.text_area('')`

This example didn't even show any effort to CSS on the `bottle` app, but `streamlit` gives it to us for free!

Additionally, the communication between frontend components and backend updates has to be tested by *you*.
And *then* you have to test the business logic.

`streamlit` has over a dozen widgets in their [input library](https://docs.streamlit.io/library/api-reference/widgets) with a team and community of developeres working on their speed, UI/UX, and resiliency.

Finally, deploying to streamlit with `streamlit run streamlit_app.py` is a valid way to run the server.
Deploying with Streamlit Sharing in the cloud is even less to deal with, netting a free Continuous Deployment pipeline from github to the cloud.

## Conclusion

While `streamlit` isn't the simplest interactive web stack out there, it very well might be the easiest.

With a growing community, new web features are added all the time to `streamlit`, but are accessible in a Pythonic way.

Are you with the majority of people who hear the word "state" and think about political geographies?
Spend some time with [session_state](https://docs.streamlit.io/library/api-reference/session-state) since the `streamlit` execution model is unique.
Soon your understanding of frontend `state` will carry over to other projects!

Want to learn what query params / arguments are for?
There's experimental support for [getting](https://docs.streamlit.io/library/api-reference/utilities/st.experimental_get_query_params) and [setting](https://docs.streamlit.io/library/api-reference/utilities/st.experimental_set_query_params) them with Python.

All that being said, if you need barebones interactivity with no dependencies, it is acheivable.
