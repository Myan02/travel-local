
$(document).ready(function() {
    // Attach a click event handler to the archive icon
    $(".archive").on("click", function() {
        // Get the post ID from the data attribute
        let postId = $(this).data("id");
 
        // Reference to the clicked element
        let $archiveButton = $(this);
 
        // Send an AJAX request to the server
        $.ajax({
            url: "/" + postId + "/archive",
            type: "POST",
            success: function(response) {
                // Update the post on the client side
                console.log("Post updated successfully", response);
 
                // Update the UI based on the server response
               if (response.success) {
                // Optionally, you can update other parts of the UI as needed
                console.log("Post archived successfully");

                // Check if the archive button was clicked on the profile page
                let isProfilePage = window.location.pathname.includes("/profile");

                // Remove the post's HTML from the UI only on the profile page
                if (isProfilePage) {
                    $archiveButton.closest(".post").remove();

                    // Check if there are no more archived posts in the left column
                    let $leftColumnArchivedPostsContainer = $(".col-md-4:first .card-body");
                    if ($leftColumnArchivedPostsContainer.children(".post").length === 0) {
                        $leftColumnArchivedPostsContainer.html("<p>No archived Posts</p>");
                    }
                }
            }
        },
            error: function(xhr, status, error) {
                console.error("Error updating post:", status, error);
            }
        });
    });
 });