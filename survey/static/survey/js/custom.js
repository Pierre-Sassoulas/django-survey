$(document).ready(function () {
  // Look for an input with date css class and load flatpickr on it, if it exists
  const dateInputFields = $("input.date");
  if (dateInputFields.length > 0) {
    dateInputFields.flatpickr();
  }
});
