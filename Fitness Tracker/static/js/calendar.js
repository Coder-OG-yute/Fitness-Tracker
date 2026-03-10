// calendar.js: recursive helpers for date calculations (countDays, generateDaysInMonth, buildMonthGrid, getDaysInMonth). note: active calendar in calendar.html may use a different approach.
// uses recursive algorithms
// Calendar helper with recursive date calculations.
// This demonstrates recursion for building calendar grids.

// The main calendar implementation is in app/templates/calendar.html, which uses
// the template from https://codepen.io/ash1198/pen/gbMPXMR
//
// These recursive functions (countDays, generateDaysInMonth, buildMonthGrid) 
// are educational examples of recursion but are not currently used by the 
// active calendar implementation in calendar.html, which uses jQuery and a 
// different approach based on the CodePen template.

// Example of a simple recursive function that counts days in a month. uses recursive algorithms
function countDays(currentDay, lastDay) {
    // Base case: when currentDay is greater than lastDay, stop.
    if (currentDay > lastDay) {
        return 0;
    }
    // Recursive case: count this day (1) plus the rest.
    return 1 + countDays(currentDay + 1, lastDay);
}

// Recursive function to generate all days in a month. uses recursive algorithms
// This builds a list of day numbers using recursion.
function generateDaysInMonth(day, lastDay, dayList) {
    // Base case: if we've passed the last day, return the list.
    if (day > lastDay) {
        return dayList;
    }
    // Recursive case: add this day to the list, then process the next day.
    dayList.push(day);
    return generateDaysInMonth(day + 1, lastDay, dayList);
}

// Helper to get the number of days in a month (accounting for leap years).
function getDaysInMonth(year, month) {
    // JavaScript months are 0-indexed (0 = January, 11 = December).
    // new Date(year, month, 0) gives the last day of the previous month,
    // so new Date(year, month + 1, 0) gives the last day of the current month.
    return new Date(year, month + 1, 0).getDate();
}

// Recursive function to build a calendar grid for a month. uses recursive algorithms
// This uses recursion to fill in days, handling the first week specially.
function buildMonthGrid(year, month, startDay, currentDay, lastDay, grid, weekIndex) {
    // Base case: if we've processed all days, return the grid.
    if (currentDay > lastDay) {
        return grid;
    }

    // Initialize the week array if needed.
    if (!grid[weekIndex]) {
        grid[weekIndex] = [];
    }

    // If this is the first week, we need to pad with empty cells
    // for days before the month starts.
    if (weekIndex === 0 && grid[weekIndex].length < startDay) {
        grid[weekIndex].push(null); // Empty cell
        return buildMonthGrid(year, month, startDay, currentDay, lastDay, grid, weekIndex);
    }

    // Add the current day to the grid.
    grid[weekIndex].push(currentDay);

    // If we've filled 7 days in this week, move to the next week.
    if (grid[weekIndex].length === 7) {
        weekIndex++;
    }

    // Recursive call for the next day.
    return buildMonthGrid(year, month, startDay, currentDay + 1, lastDay, grid, weekIndex);
}

// Main function to generate a month calendar.
function generateMonthCalendar(year, month) {
    // Get the first day of the month and what day of the week it falls on.
    const firstDay = new Date(year, month, 1);
    const startDayOfWeek = firstDay.getDay(); // 0 = Sunday, 6 = Saturday

    const lastDay = getDaysInMonth(year, month);
    const grid = [];

    // Use recursion to build the calendar grid.
    buildMonthGrid(year, month, startDayOfWeek, 1, lastDay, grid, 0);

    return grid;
}

// Example usage when the page loads:
document.addEventListener('DOMContentLoaded', function() {
    // If we're on a calendar page, we could generate the current month.
    // For now, this is just a demonstration of the recursive functions.
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth();

    // You can call generateMonthCalendar(currentYear, currentMonth) to get a grid.
    // This would be used by the calendar.html template to display days.
});
