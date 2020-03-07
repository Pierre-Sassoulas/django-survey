/* globals $ */

$(document).ready(function () {
  // Look for a input with date css class and load flatpickr on it, if it exists
  const inputFields = $('input.date')
  if (inputFields.length > 0) {
    inputFields.flatpickr()
  }
})
