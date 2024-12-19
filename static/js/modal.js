'use strict';
        
        document.addEventListener('DOMContentLoaded', function() {
            const modal = document.querySelector('.modal');
            const overlay = document.querySelector('.overlay');
            const btnCloseModal = document.querySelector('.close-modal');
            const btnsOpenModal = document.querySelector('.show-modal');

            const openModal = function (e) {
                e.preventDefault(); // Add this to prevent default link behavior
                modal.classList.remove('hidden');
                overlay.classList.remove('hidden');
            };

            const closeModal = function () {
                modal.classList.add('hidden');
                overlay.classList.add('hidden');
            };

            btnCloseModal.addEventListener('click', closeModal);
            overlay.addEventListener('click', closeModal);
            btnsOpenModal.addEventListener('click', openModal);

            // Add keyboard event listener for Escape key
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    closeModal();
                }
            });
        });