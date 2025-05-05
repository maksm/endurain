// Helper functions for date calculations, assuming Monday is the start of the week

/**
 * Gets the start date (Monday) of the week for a given date.
 * @param {Date} d - The input date.
 * @returns {Date} - The date of the Monday of that week.
 */
export function getWeekStartDate(d) {
  const date = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const day = date.getUTCDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
  const diff = date.getUTCDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
  return new Date(date.setUTCDate(diff));
}

/**
 * Gets the end date (Sunday + 1 day for exclusive range) of the week for a given date.
 * @param {Date} d - The input date.
 * @returns {Date} - The date representing the start of the next week.
 */
export function getWeekEndDate(d) {
  const startDate = getWeekStartDate(d);
  const endDate = new Date(startDate);
  endDate.setUTCDate(startDate.getUTCDate() + 7);
  return endDate;
}

/**
 * Gets the start date (1st) of the month for a given date.
 * @param {Date} d - The input date.
 * @returns {Date} - The date of the first day of that month.
 */
export function getMonthStartDate(d) {
   return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1));
}

/**
 * Gets the end date (1st of next month) of the month for a given date.
 * @param {Date} d - The input date.
 * @returns {Date} - The date representing the start of the next month.
 */
export function getMonthEndDate(d) {
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1));
}

/**
 * Formats a Date object into YYYY-MM-DD string.
 * @param {Date} date - The input date.
 * @returns {string} - The formatted date string.
 */
export function formatDateISO(date) {
    // Ensure input is a Date object
    if (!(date instanceof Date)) {
        console.error("formatDateISO received non-Date object:", date);
        // Attempt to parse if it's a valid date string, otherwise return empty or throw
        try {
            date = new Date(date);
            if (isNaN(date.getTime())) throw new Error("Invalid date input");
        } catch (e) {
            return ""; // Or handle error appropriately
        }
    }
    // Check for invalid date after potential parsing
    if (isNaN(date.getTime())) {
        console.error("formatDateISO received invalid Date object:", date);
        return "";
    }
    return date.toISOString().slice(0, 10);
}

/**
 * Gets the ISO week number for a given date.
 * @param {Date} date - The input date.
 * @returns {number} - The ISO week number.
 */
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  // Set to nearest Thursday: current date + 4 - current day number
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  // Get first day of year
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  // Calculate full weeks to nearest Thursday
  const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return weekNo;
}

/**
 * Parses a "YYYY-Www" string into the Date object for the Monday of that week.
 * Note: Accuracy depends on consistent ISO 8601 week date interpretation.
 * @param {string} weekString - The week string (e.g., "2023-W42").
 * @returns {Date} - The Date object for the start of the week (Monday UTC).
 */
export function parseWeekString(weekString) {
    const match = weekString.match(/^(\d{4})-W(\d{1,2})$/);
    if (!match) throw new Error(`Invalid week string format: ${weekString}`);
    const year = parseInt(match[1], 10);
    const week = parseInt(match[2], 10);

    // Calculate the date of the first day of the year
    const firstDayOfYear = new Date(Date.UTC(year, 0, 1));
    // Get the day of the week for the first day (0=Sun, 1=Mon...)
    const firstDayOfWeek = firstDayOfYear.getUTCDay() || 7; // Adjust Sunday (0) to 7

    // Calculate the date of the first Monday of the year
    // If Jan 1 is Mon-Thu, the first week starts in this year.
    // If Jan 1 is Fri-Sun, the first week starts in the previous year, but week 1 starts on the first Monday.
    let daysOffset = (week - 1) * 7; // Days from start of week 1
    if (firstDayOfWeek <= 4) {
        // First day is Mon-Thu, week 1 starts with this week's Monday
        daysOffset += (1 - firstDayOfWeek);
    } else {
        // First day is Fri-Sun, week 1 starts next Monday
        daysOffset += (8 - firstDayOfWeek);
    }

    const targetDate = new Date(Date.UTC(year, 0, 1 + daysOffset));
    return targetDate;
}


/**
 * Parses a "YYYY-MM" string into the Date object for the 1st of that month.
 * @param {string} monthString - The month string (e.g., "2023-10").
 * @returns {Date} - The Date object for the start of the month (1st day UTC).
 */
export function parseMonthString(monthString) {
    const match = monthString.match(/^(\d{4})-(\d{1,2})$/);
    if (!match) throw new Error(`Invalid month string format: ${monthString}`);
    const year = parseInt(match[1], 10);
    const month = parseInt(match[2], 10); // 1-based month
    // Date.UTC expects 0-based month
    return new Date(Date.UTC(year, month - 1, 1));
}

/**
 * Formats a Date object into a "YYYY-Www" string.
 * @param {Date} date - The input date.
 * @returns {string} - The formatted week string.
 */
export function formatDateToWeekString(date) {
    const monday = getWeekStartDate(date); // Ensure we use the start of the week
    const year = monday.getUTCFullYear();
    const week = getWeekNumber(monday);
    // Handle edge case where week number belongs to the previous/next year
    const firstDayOfYear = new Date(Date.UTC(year, 0, 1));
    const dayOfYear = Math.floor((monday - firstDayOfYear) / 86400000);

    let displayYear = year;
    // If it's early January but belongs to the last week of the previous year
    if (week >= 52 && monday.getUTCMonth() === 0) {
        displayYear = year - 1;
    }
    // If it's late December but belongs to the first week of the next year
    // This case is less common with getWeekStartDate ensuring Monday, but good to be aware of
    // getWeekNumber should handle the year correctly based on Thursday rule.

    // Ensure week number is padded
    const paddedWeek = week < 10 ? `0${week}` : `${week}`;
    return `${displayYear}-W${paddedWeek}`;
}


/**
 * Formats a Date object into a "YYYY-MM" string.
 * @param {Date} date - The input date.
 * @returns {string} - The formatted month string.
 */
export function formatDateToMonthString(date) {
    const year = date.getUTCFullYear();
    const month = date.getUTCMonth() + 1; // 0-based to 1-based
    const paddedMonth = month < 10 ? `0${month}` : `${month}`;
    return `${year}-${paddedMonth}`;
}
