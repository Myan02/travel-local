$(document).ready(function() {
   // Attach a click event handler to the archive icon
   $(".archive").on("click", function() {
       // Get the post ID from the data attribute
       let postId = $(this).data("id");

       // Send an AJAX request to the server
       $.ajax({
           url: "/"+postId+"/archive",
           type: "POST",
           success: function(response) {
               // Update the post on the client side if needed
               console.log("Post updated successfully", response);
           },
           error: function(xhr, status, error) {
               console.error("Error updating post:", status, error);
           }
       });
   });
});