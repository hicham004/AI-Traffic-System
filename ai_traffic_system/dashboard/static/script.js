
function updateLights() {
  fetch('/api/lights')
    .then(res => res.json())
    .then(data => {
      ['north', 'south', 'east', 'west'].forEach(dir => {
        const el = document.getElementById('light-' + dir);
        el.className = 'light ' + data[dir].toLowerCase();
      });
    });
}

function triggerCycle() {
  fetch('/api/sim/next')
    .then(() => updateLights());
}

setInterval(updateLights, 1000);
