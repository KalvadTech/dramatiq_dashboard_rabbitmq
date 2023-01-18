// Delete message
function msg_delete(queue_name, message_id) {
    if (confirm("Are you sure you want to delete this message?")) {
        // Send a DELETE request to the server using the fetch API
        fetch("/api/queue/" + queue_name + '/message/' + message_id, {
            method: "DELETE"
        })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("There was an error deleting the message. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("There was an error deleting the message. Please try again.");
            });
    }
}

// Requeue message
function msg_requeue(queue_name, message_id) {
    if (confirm("Are you sure you want to requeue this message?")) {
        // Send a PUT request to the server using the fetch API
        fetch("/api/queue/" + queue_name + '/message/' + message_id + '/requeue', {
            method: "PUT"
        })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert("There was an error requeueing the message. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("There was an error requeueing the message. Please try again.");
            });
    }
}

function refreshPage() {
    setTimeout(function () {
        location.reload();
    }, 5000);
}

refreshPage();