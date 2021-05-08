const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')
const submitButton = document.getElementById('submit-button')

char_length.addEventListener('input', validateChars)

async function getCharStream(){
  try {
    if(!start_string.value || !temp.value || !char_length.value){
      return output.innerHTML = 'Please fill in all input fields.'
    }
    submitButton.setAttribute('disabled', true)

    const reqData = JSON.stringify({
      start_string: start_string.value,
      temp: temp.value,
      char_length: char_length.value,
    })
    const res = await fetch('/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Connection': 'keep-alive'
      },
      body: reqData
    })

    const decoder = new TextDecoder('utf-8')
    const generator = streamGenerator(res.body)
    output.innerHTML = `${start_string.value}`

    for await (const chunk of generator) {
      const result = decoder.decode(chunk)
      output.innerHTML += result
    }
    submitButton.removeAttribute('disabled')
  } catch(err){
    console.log('getCharStream err', err)
    output.innerHTML = `Error: ${err.message}`
  }
}

async function* streamGenerator(stream){
  const reader = stream.getReader()
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        return
      }
      yield value
    }
  } catch(err) {
    throw err
  } finally {
    reader.releaseLock()
  }
}

function validateChars(e){
  const val = e.target.value;
  let numVal = Number(val)
  if(isNaN(numVal)){
    e.preventDefault()
    e.target.value = 1000
    return
  }
  if(val.length > 4){
    e.preventDefault()
    e.target.value = val.substring(0, 4)
    return
  }
}
