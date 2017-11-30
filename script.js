/*** KONAMI CODE ***/
var allowedKeys = {
 	37: 'left',
 	38: 'up',
 	39: 'right',
	40: 'down',
	65: 'a',
	66: 'b'
};

var konamiCode = ['up', 'up', 'down', 'down', 'left', 'right', 'left', 'right', 'b', 'a'];
var konamiCodePosition = 0;

document.addEventListener('keydown', function(e) {
	var key = allowedKeys[e.keyCode];
	var requiredKey = konamiCode[konamiCodePosition];

	// compare entered key with required key
	if (key == requiredKey) {
		konamiCodePosition++;
		if (konamiCodePosition == konamiCode.length)
			activateCheat();
	}
	else konamiCodePosition = 0;
});

function activateCheat() {
	window.location = "https://www.youtube.com/embed/6M6samPEMpM?rel=0&autoplay=1";
}
