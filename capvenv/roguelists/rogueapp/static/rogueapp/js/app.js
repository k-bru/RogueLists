document.addEventListener("DOMContentLoaded", function () {
  const collapsedHeaders = document.querySelectorAll('.list-holder h2.collapsed');
  for (let header of collapsedHeaders) {
    header.classList.remove('collapsed');
    header.classList.add('show');
  }
});

document.querySelectorAll('select[name="tier_rank"]').forEach(function (select) {
  select.addEventListener('change', function () {
    this.closest('form').submit();
  });
});

function goBack() {
  window.history.back();
}