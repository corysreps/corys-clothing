// This file contains the JavaScript code for the application, adding interactivity to the index page.

document.addEventListener('DOMContentLoaded', function() {
    const greetingElement = document.getElementById('greeting');
    greetingElement.textContent = 'Welcome to the Flask Web App!';
    
    const button = document.getElementById('clickMe');
    button.addEventListener('click', function() {
        alert('Button clicked!');
    });
});