const output = document.getElementById('output')
const start_string = document.getElementById('start_string')
const temp = document.getElementById('temperature')
const char_length = document.getElementById('char_length')

temp.addEventListener('input', validateInput)
char_length.addEventListener('input', validateChars)

function generate(){
    if(start_string.value && temp.value && char_length.value){
      output.innerHTML = 'Generating...'
      let obj = {
        start_string: start_string.value,
        temp: temp.value || 0.6,
        char_length: char_length.value || 600,
      }
      return fetch('/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(obj),
      }).then(res => res.json()).then(data => {
        output.innerHTML = data.result
      }).catch(err => {
        output.innerHTML = 'Request timeout. Try setting the character length value lower.'
        console.log('err', err)
    })
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
