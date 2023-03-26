document.addEventListener("DOMContentLoaded", function () {
  showCollapsedHeaders('.list-holder h2.collapsed');
  hideCollapsedHeaders('.sort-holder h2.show');

  document.querySelectorAll('select[name="tier_rank"]').forEach(function (select) {
    select.addEventListener('change', function () {
      this.closest('form').submit();
    });
  });
});

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

addEditNameAndDescriptionListeners();
