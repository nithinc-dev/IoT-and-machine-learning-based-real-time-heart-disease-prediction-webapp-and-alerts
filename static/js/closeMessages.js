// // closeMessages.js
// 'use strict';

// document.addEventListener('DOMContentLoaded', function() {
//     const messageElements = document.querySelectorAll('.messages');
    
//     messageElements.forEach(message => {
//         const exitButton = message.querySelector('.exit-message');
        
//         exitButton.addEventListener('click', function() {
//             message.classList.add('hidden');
//         });

//         // Optional: Auto-hide messages after 5 seconds
//         setTimeout(() => {
//             message.classList.add('hidden');
//         }, 5000);
//     });
// });



'use strict';


// const messages = document.querySelector('.messages');
// const btnCloseModal = document.querySelector('.messages-exit');
// const closeMessages = function () {
//     messages.classList.add('hidden');
//   };
// btnCloseModal.addEventListener('click', closeMessages);


const messages = document.querySelector('.messages');
// const btnCloseModal = document.querySelector('.messages-exit');
const closeMessages = function () {
    messages.classList.add('hidden');
  };
messages.addEventListener('click', closeMessages);