document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const filterForm = document.getElementById('filterForm');
    const combinedForm = document.createElement('form');
    combinedForm.style.display = 'none';
    document.body.appendChild(combinedForm);

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        combineForms();
        combinedForm.submit();
    });

    filterForm.addEventListener('submit', function(event) {
        event.preventDefault();
        combineForms();
        combinedForm.submit();
    });

    function combineForms() {
        combinedForm.innerHTML = '';
        const searchInputs = searchForm.querySelectorAll('input, select, textarea');
        const filterInputs = filterForm.querySelectorAll('input, select, textarea');

        searchInputs.forEach(input => {
            const newInput = document.createElement('input');
            newInput.type = 'hidden';
            newInput.name = input.name;
            newInput.value = input.value;
            combinedForm.appendChild(newInput);
        });

        filterInputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                if (input.checked) {
                    const newInput = document.createElement('input');
                    newInput.type = 'hidden';
                    newInput.name = input.name;
                    newInput.value = input.value;
                    combinedForm.appendChild(newInput);
                }
            } else {
                const newInput = document.createElement('input');
                newInput.type = 'hidden';
                newInput.name = input.name;
                newInput.value = input.value;
                combinedForm.appendChild(newInput);
            }
        });
    }
});