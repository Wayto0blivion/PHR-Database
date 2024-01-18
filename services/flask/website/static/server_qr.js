/**
 * Represents the selected result object.
 *
 * @typedef {Object} SelectedResult
 *
 * @property {any} [property1] - The first property of the selected result.
 * @property {any} [property2] - The second property of the selected result.
 * @property {any} [...] - Additional properties of the selected result.
 */
let selectedResult = {}

$(document).ready(function(){

    $(document).on('show.bs.modal', '#quantityModal', function (event) {

        alert("Modal Shown");

        let button = $(event.relatedTarget); // Button that triggered the modal
        selectedResult.pid = button.data('pid');
        selectedResult.make = button.data('make');
        selectedResult.model = button.data('model');

    });

    $("button[data-toggle='modal']").click(function() {
        /**
         * Retrieves the pid (process ID) of the selected result.
         *
         * @returns {number} The pid of the selected result.
         */
        selectedResult.pid = $(this).data('pid');
        selectedResult.make = $(this).data('make');
        selectedResult.model = $(this).data('model');

        console.log("Direct button click - PID: ", selectedResult.pid);
        console.log("Direct button click - Make: ", selectedResult.make);
        console.log("Direct button click - Model: ", selectedResult.model);
    });


    $('#saveQuantity').click(function() {
        let quantity = $('#quantity').val();
        // let csrf_token = $('meta[name="csrf-token"]').attr('content'); // Get the csrf token stored in a meta tag.
        let csrf_token = $('#quantityForm input[name="csrf_token"]').val();
        console.log('Quantity: ', quantity);
        console.log('Selected Result: ', selectedResult);

        if (quantity > 0) {
            $.ajax({
                url: '/add-to-session',
                type: 'POST',
                headers: {
                  'X-CSRFToken': csrf_token
                },
                contentType: 'application/json',
                data: JSON.stringify({quantity: quantity, ...selectedResult}),
                dataType: 'json',
                success: function(response) {
                    // Handle Response
                    console.log(response.message);
                    // Print the contents of the session variable, which
                    // contains all selected addons, and print it to the div.
                    let sessionDiv = $('#sessionDiv');
                    sessionDiv.text(response.message);
                },
                error: function(xhr, status, error) {
                    // Handle error
                    console.error('AJAX Error:', error);
                    console.error('Status:', status);
                    console.error('Response:', xhr.responseText);
                }
            });

        //     Add the selected addon to the database.

        }
    });
});


