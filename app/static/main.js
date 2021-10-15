const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')
const SubmitButton = document.getElementById('submit-button')
const baseUrl = window.location.host.includes('xfilesgenerator.com')
  ? 'wss://xfilesgenerator.com'
  : 'ws://127.0.0.1:8000'

var content = ''

char_length.addEventListener('input', validateChars)

const client_id = Date.now()
const socket = new WebSocket(`${baseUrl}/ws/${client_id}`)

socket.onconnect = (e) => console.log('connected: ', e)
socket.ondisconnect = (e) => console.log('disconnected:', e)
socket.onerror = (e) => console.log('error', e)
socket.onmessage = (e) => {
  content += e.data
  output.innerHTML = content.replace("�", "")
}

SubmitButton.addEventListener('click', submit)

async function submit() {
  if (!start_string.value || start_string.value.length === 0) {
    return output.innerHTML = 'Please fill in all input fields.'
  }
  content = `${start_string.value}`
  const payload = JSON.stringify({
    start_string: start_string.value,
    temp: temp.value,
    char_length: char_length.value || 500
  })
  await socket.send(payload)
  output.innerHTML = content
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
