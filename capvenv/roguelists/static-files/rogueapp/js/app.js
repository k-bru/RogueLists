
/**
 Displays collapsed headers for the specified selector. Used for areas that are shown by default.
 @param {string} selector - The CSS selector for the collapsed headers. 
 */
function showCollapsedHeaders(selector) {
  const collapsedHeaders = document.querySelectorAll(selector);
  for (let header of collapsedHeaders) {
    header.classList.remove('collapsed');
    header.classList.add('show');
  }
}

/**
 Hides collapsed headers for the specified selector. Used for areas that are collapsed by default.
 @param {string} selector - The CSS selector for the collapsed headers.
 */
function hideCollapsedHeaders(selector) {
  const collapsedHeaders = document.querySelectorAll(selector);
  for (let header of collapsedHeaders) {
    header.classList.remove('show');
    header.classList.add('collapsed');
  }
}

/**
 * Function to go back to previous page in browser history
*/
function goBack() {
  window.history.back();
}

/**
 * Function to add event listeners to the edit name and description icons and toggle their visibility
*/
function addEditNameAndDescriptionListeners() {
  const editNameIcon = document.getElementById('edit-name-icon');
  const editDescriptionIcon = document.getElementById('edit-description-icon');
  const nameInputContainer = document.getElementById('name-input-container');
  const descriptionInputContainer = document.getElementById('description-input-container');
  
  editNameIcon.addEventListener('click', () => {
    nameInputContainer.classList.toggle('d-none');
  });
  
  editDescriptionIcon.addEventListener('click', () => {
    descriptionInputContainer.classList.toggle('d-none');
  });
}
/**
 *  When the user scrolls down 20px from the top of the document, show the button
*/
function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementById("back-to-top").style.display = "block";
  } else {
    document.getElementById("back-to-top").style.display = "none";
  }
}

/**
 * When the user clicks on the button, scroll to the top of the document
*/
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

/**
 * Function to update search results on users page
*/
function searchUsers() {
  const userNames = document.querySelectorAll('.user-name');
  const userSearch = document.querySelector('#user-search');
  
  userSearch.addEventListener('input', () => {
    const query = userSearch.value.toLowerCase();
    userNames.forEach((userName) => {
      const name = userName.textContent.toLowerCase();
      if (name.includes(query)) {
        userName.style.display = 'inline-block';
      } else {
        userName.style.display = 'none';
      }
    });
  });
}

/**
 * Adds event listeners and initializes the page on DOMContentLoaded.
 * 
 */
document.addEventListener("DOMContentLoaded", function () {
  // Show collapsed headers that are initially hidden.
  showCollapsedHeaders('.list-holder h2.collapsed');

  // Hide collapsed headers that are initially displayed.
  hideCollapsedHeaders('.sort-holder h2.show');
  
  // Allow for edits of list names and descriptions.
  addEditNameAndDescriptionListeners();

  // Update search results on users page
});

// Add change event listeners to 'tier_rank' select dropdowns.
document.querySelectorAll('select[name="tier_rank"]').forEach(function (select) {
  select.addEventListener('change', function () {
    // Submit the form closest to the dropdown when the value is changed
    this.closest('form').submit();
  });
});

//Back to top button
window.onscroll = function () { scrollFunction() };
searchUsers();
