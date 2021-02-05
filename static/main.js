const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')

temp.addEventListener('input', validateInput)
char_length.addEventListener('input', validateChars)

async function getCharStream(){
  try {
    if(start_string.value && temp.value && char_length.value){
      const reqData = {
        start_string: start_string.value,
        temp: temp.value,
        char_length: char_length.value,
      }
      const res = await fetch('/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Connection': 'keep-alive'
        },
        body: JSON.stringify(reqData),
      })
      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8')
      let result = `${start_string.value}`

      const stream = await new ReadableStream({
        start(controller) {
          push();
          function push() {
            return reader.read().then(({ done, value }) => {
              if(done){
                controller.close()
                return
              }
              const chunk = decoder.decode(value)
              controller.enqueue(chunk)
              result += chunk
              output.innerHTML = result
              push()
            })
          }
        }
      })
      return new Response(stream);
    }
    return output.innerHTML = 'Please fill in all input fields.'
  } catch(err){
    console.log('getCharStream err', err)
    output.innerHTML = `Error: ${err.message}`
  }
}

function validateInput(e){
  const val = e.target.value;
  let numVal = Number(val)
  if(isNaN(numVal)){
    e.preventDefault()
    e.target.value = 0.6
    return
  }
  if(val.length > 4){
    e.preventDefault()
    e.target.value = val.substring(val.indexOf('0.'), 4)
    return
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
