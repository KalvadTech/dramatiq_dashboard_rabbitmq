import Swal from 'sweetalert2';

(window as any).msg_delete = (queue_name: string, message_id: string) => {
    // stops the refresh time and shows an alert to the user if the users presses yes then delete the
    // msg from the queue and refresh the page using ajax, if an error is encountered show an error alert
    clearInterval(window.myApp.refreshIntervalId);
    Swal.fire({
        title: 'Are you sure you want to delete this message?',
        showDenyButton: true,
        confirmButtonText: 'Yes',
        denyButtonText: `No`,
        background: window.myApp.elementBackground,
        color: window.myApp.elementColor,
    }).then(async (result) => {
        if (result.isConfirmed) {
            // Create a headers object and add the Authorization header
            const headers = new Headers();
            const auth = (document.getElementById("credentials") as HTMLInputElement).value;
            headers.append('Authorization', `Basic ${auth}`);
            const options = {
                method: "DELETE",
                headers: headers
            };
            try {
                const res = await fetch("/api/queue/" + queue_name + '/message/' + message_id, options);
                if (res.ok) {
                    location.reload();
                } else {
                    Swal.fire({
                        icon: 'error', text: "There was an error deleting the message. Please try again.",
                        background: window.myApp.elementBackground,
                        color: window.myApp.elementColor,
                    });
                }
            } catch (error) {
                console.error("Error:", error);
                Swal.fire({
                    icon: 'error', text: "There was an error deleting the message. Please try again.",
                    background: window.myApp.elementBackground,
                    color: window.myApp.elementColor,
                });
            }
        } else {
            window.refreshPage();
        }
    });
};

(window as any).msg_requeue = (queue_name: string, message_id: string) => {
    // stops the refresh time and shows an alert to the user if the users presses yes then requeue the
    // msg and refresh the page using ajax, if an error is encountered show an error alert
    clearInterval(window.myApp.refreshIntervalId);
    Swal.fire({
        title: 'Are you sure you want to requeue this message?',
        showDenyButton: true,
        confirmButtonText: 'Yes',
        denyButtonText: `No`,
        background: window.myApp.elementBackground,
        color: window.myApp.elementColor,
    }).then(async (result) => {
        if (result.isConfirmed) {
            // Create a headers object and add the Authorization header
            const headers = new Headers();
            const auth = (document.getElementById("credentials") as HTMLInputElement).value;
            headers.append('Authorization', `Basic ${auth}`);
            const options = {
                method: "PUT",
                headers: headers
            };
            try {
                const res = await fetch("/api/queue/" + queue_name + '/message/' + message_id + '/requeue', options);
                if (res.ok) {
                    location.reload();
                } else {
                    Swal.fire({
                        icon: 'error', text: "There was an error requeueing the message. Please try again.",
                        background: window.myApp.elementBackground,
                        color: window.myApp.elementColor,
                    });
                }
            } catch (error) {
                console.error("Error:", error);
                Swal.fire({
                    icon: 'error', text: "There was an error requeueing the message. Please try again.",
                    background: window.myApp.elementBackground,
                    color: window.myApp.elementColor,
                });
            }
        } else {
            window.refreshPage();
        }
    });
};
