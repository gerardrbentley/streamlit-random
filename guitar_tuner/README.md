# Streamlit Guitar Tuner

Powered by [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)

Made with ❤️ from [Gar's Bar](https://tech.gerardbentley.com/)

## What is this?

A simplified guitar tuner built with [Streamlit](https://streamlit.io).
Sends the sound from your device's microphone (after you hit *Start*) then processes it to find the nearest open guitar note.

This only finds one peak frequency, so if you have background noise it won't work well.

Low strings will probably get washed out by mic noise or natural harmonics (fundamental frequency isn't the peak sometimes).
Feel free to [research](https://music.stackexchange.com/questions/101677/why-is-the-5th-stronger-than-the-1st-in-guitar-spectrum) and [experiment](https://makersportal.com/blog/2018/9/20/audio-processing-in-python-part-iii-guitar-string-theory-and-frequency-analysis) with these resources.

## Local Dev

`pip install -r webrequirements.txt`

If this fails (couldn't get everything working easily on mac for me. conda for just opencv, pip for other things?), feel free to try with docker:

`docker-compose up`

add `--build` if you change requirements after closing with `ctrl+c`

add `-d` to get your terminal back (be sure to `docker-compose down` at some point to turn it off)

*BONUS:* use `docker-compose exec streamlit-app bash` after you have run `up` to get a shell in your streamlit app.
Ex: to `pip list` dependency versions
