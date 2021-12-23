const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
// const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')
const SubmitButton = document.getElementById('submit-button')
const baseUrl = window.location.host.includes('xfilesgenerator.com')
  ? 'wss://xfilesgenerator.com'
  : 'ws://127.0.0.1:8000'

var socket

class AsyncWebSocket extends WebSocket {
  async *[Symbol.asyncIterator]() {
    while (this.readyState !== 3) {
      yield (await oncePromise(this, 'message')).data
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  listen()
  char_length.addEventListener('input', validateChars)
  SubmitButton.addEventListener('click', submit)
})

async function listen() {
  const client_id = Date.now()
  socket = new AsyncWebSocket(`${baseUrl}/ws/${client_id}`)
  for await (let message of socket) {
    handleMessage(message)
  }
}

function handleMessage(data) {
  output.innerHTML += data
}

function oncePromise(emitter, event) {
  return new Promise(resolve => {
    var handler = (...args) => {
      emitter.removeEventListener(event, handler)
      resolve(...args);
    }
    emitter.addEventListener(event, handler)
  })
}

function submit() {
  if (!start_string.value || start_string.value.length === 0) {
    return output.innerHTML = 'Please fill in all input fields.'
  }

  const payload = JSON.stringify({
    start_string: start_string.value,
    char_length: char_length.value
  })

  if (socket?.readyState === 1) {
    socket.send(payload)
    output.innerHTML = `${start_string.value}`
  }
}

function validateChars(e){
  const val = e.target.value
  const numVal = Number(val)
  if (isNaN(numVal)) {
    e.preventDefault()
    e.target.value = 200
    return
  }
  if (numVal > 1000) {
    e.preventDefault()
    e.target.value = 200
    return
  }
}
