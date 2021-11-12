const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
// const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')
const SubmitButton = document.getElementById('submit-button')
const baseUrl = window.location.host.includes('xfilesgenerator.com')
  ? 'wss://xfilesgenerator.com'
  : 'ws://127.0.0.1:8000'

var content = ''
var socket
var PIPELINE_MODE = false

WebSocket.prototype[Symbol.asyncIterator] = async function*() {
  while (this.readyState !== 3) {
    yield (await oncePromise(this, 'message')).data
  }
}

const listen = async () => {
  const client_id = Date.now()
  socket = new WebSocket(`${baseUrl}/ws/${client_id}`)
  for await (let message of socket) {
    handleMessage(message)
  }
}

listen()
char_length.addEventListener('input', validateChars)
SubmitButton.addEventListener('click', submit)

function handleMessage(data) {
  if (PIPELINE_MODE) {
    output.innerHTML = data
  } else {
    content += data
    output.innerHTML = content
  }
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
  content = ''
  if (!start_string.value || start_string.value.length === 0) {
    return output.innerHTML = 'Please fill in all input fields.'
  }
  PIPELINE_MODE = (Number(char_length.value) > 300)

  const payload = JSON.stringify({
    start_string: start_string.value,
    char_length: char_length.value,
    pipeline: PIPELINE_MODE
  })
  if (!PIPELINE_MODE) content = `${start_string.value}`
  if (socket?.readyState === 1) {
    socket.send(payload)
    output.innerHTML = content
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
  if (numVal > 5000) {
    e.preventDefault()
    e.target.value = 200
    return
  }
}
