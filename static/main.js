const output = document.getElementById('output')
const start_string = document.getElementById('start_string').value
const temp = document.getElementById('temperature').value
const char_el = document.getElementById('char_length')
const char_length = char_el.value
const submitButton = document.getElementById('submit-button')
const decoder = new TextDecoder('utf-8')

window.addEventListener('DOMContentLoaded', async () => {
  await initStream()
})

submitButton.addEventListener('click', async () => {
  await initStream()
})

char_el.addEventListener('input', validateChars)

async function initStream(){
  if (start_string && temp && char_length) {
    await getCharStream()
  } else {
    return output.innerHTML = 'Please fill in all input fields.'
  }
}

async function getCharStream(){
  submitButton.setAttribute('disabled', true)
  try {
    const res = await fetch('/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive'
      },
      body: JSON.stringify({ start_string, temp, char_length })
    })
    const generator = streamGenerator(res.body, decoder)
    output.innerHTML = `${start_string}`
    for await (const chunk of generator) {
      output.innerHTML += chunk
    }
  } catch(err){
    console.error(err)
    output.innerHTML = `Error: ${err.message}`
  } finally {
    submitButton.removeAttribute('disabled')
  }
}

async function* streamGenerator(stream, decoder){
  const reader = stream.getReader()
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        return
      }
      yield decoder.decode(value)
    }
  } catch(err) {
    throw err
  } finally {
    reader.releaseLock()
  }
}

function validateChars(e){
  const val = e.target.value
  const numVal = Number(val)
  if(isNaN(numVal)){
    e.preventDefault()
    e.target.value = 1000
    return
  }
  if (val.length > 4) {
    e.preventDefault()
    e.target.value = val.substring(0, 4)
    return
  }
}
