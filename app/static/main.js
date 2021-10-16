const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')
const SubmitButton = document.getElementById('submit-button')
const baseUrl = window.location.host.includes('xfilesgenerator.com')
  ? 'wss://xfilesgenerator.com'
  : 'ws://127.0.0.1:8000'

var content = ''
var socket

window.addEventListener('DOMContentLoaded', () => {
  initSocket()
  SubmitButton.addEventListener('click', submit)
})

char_length.addEventListener('input', validateChars)

function initSocket() {
  const client_id = Date.now()
  socket = new WebSocket(`${baseUrl}/ws/${client_id}`)

  socket.addEventListener('open', () => {
    console.log('connected')
  })
  socket.addEventListener('message', (e) => {
    handleMessage(e.data)
  })
  socket.addEventListener('close', () => {
    console.log('disconnected')
  })
  socket.addEventListener('error', (e) => {
    console.log('error: ', e)
  })
}

function handleMessage(data) {
  content += data
  output.innerHTML = content
}

function submit() {
  if (!start_string.value || start_string.value.length === 0) {
    return output.innerHTML = 'Please fill in all input fields.'
  }
  content = `${start_string.value}`
  const payload = JSON.stringify({
    start_string: start_string.value,
    temp: temp.value,
    char_length: char_length.value || 500
  })
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
    e.target.value = 500
    return
  }
  if (val.length > 4) {
    e.preventDefault()
    e.target.value = val.substring(0, 4)
    return
  }
}
