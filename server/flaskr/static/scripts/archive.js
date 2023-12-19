$(document).ready(function() {
    $(".archive").on("click", function() {
        let postId = $(this).data("id");
        let $archiveButton = $(this);
 
        $.ajax({
            url: "/" + postId + "/archive",
            type: "POST",
            success: function(response) {
                console.log("Post updated successfully", response);
 
                if (response.success) {
                console.log("Post archived successfully");

                let isProfilePage = window.location.pathname.includes("/profile");

                if (isProfilePage) {
                    $archiveButton.closest(".post").remove();

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