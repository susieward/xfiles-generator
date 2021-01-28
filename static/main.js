
// Select the node that will be observed for mutations
const targetNode = document.getElementById('output-content');

console.log('targetNode', targetNode)
// Options for the observer (which mutations to observe)
const config = { attributes: true, childList: true, subtree: true };

// Callback function to execute when mutations are observed
const callback = function(mutationsList, observer){
  for(const mutation of mutationsList){
    if(mutation.type === 'childList'){
      console.log(targetNode.innerText)
      //console.log('A child node has been added or removed.');
    }
  }
};

// Create an observer instance linked to the callback function
const observer = new MutationObserver(callback);

// Start observing the target node for configured mutations
observer.observe(targetNode, config);
