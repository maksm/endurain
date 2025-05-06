<template>
  <div class="container mt-4">
    <h2>{{ t('summaryView.title') }}</h2>

    <!-- Controls Section -->
    <div class="row mb-3 align-items-end">
      <!-- Activity Type Filter -->
      <div class="col-md-3">
        <label for="activityTypeFilter" class="form-label">{{ t('summaryView.filterLabelActivityType') }}</label>
        <select id="activityTypeFilter" class="form-select" v-model="selectedActivityType" :disabled="loadingTypes">
          <option value="">{{ t('summaryView.filterOptionAllTypes') }}</option>
          <!-- Iterate over dictionary items: key is ID, value is Name -->
          <option v-for="(name, id) in activityTypes" :key="id" :value="id">{{ name }}</option>
        </select>
        <!-- Optional: Add loading/error state for types -->
         <div v-if="loadingTypes" class="form-text">{{ t('summaryView.loading') }}...</div>
         <div v-if="errorTypes" class="form-text text-danger">{{ errorTypes }}</div>
      </div>
      <!-- View Type Filter -->
      <div class="col-md-3">
        <label for="viewType" class="form-label">{{ t('summaryView.labelViewType') }}</label>
        <select id="viewType" class="form-select" v-model="selectedViewType">
          <option value="week">{{ t('summaryView.optionWeekly') }}</option>
          <option value="month">{{ t('summaryView.optionMonthly') }}</option>
          <option value="year">{{ t('summaryView.optionYearly') }}</option>
          <option value="lifetime">{{ t('summaryView.optionLifetime') }}</option>
        </select>
      </div>
      <div class="col-md-3" v-if="selectedViewType !== 'lifetime'">
         <label :for="periodInputId" class="form-label">{{ periodLabel }}</label>
         <!-- Conditional Input Types -->
         <!-- Use type="date" for week selection -->
         <input type="date" :id="periodInputId" class="form-control" v-if="selectedViewType === 'week'" v-model="selectedDate" @change="handleDateInputChange">
         <!-- Use type="month" for month selection -->
         <input type="month" :id="periodInputId" class="form-control" v-else-if="selectedViewType === 'month'" v-model="selectedPeriodString">
         <!-- Use type="number" for year selection -->
         <input type="number" :id="periodInputId" class="form-control" v-else-if="selectedViewType === 'year'" v-model.number="selectedYear" placeholder="YYYY" min="1900" max="2100">
      </div>
      <!-- Add navigation buttons -->
       <div class="col-md-3 d-flex align-items-end" v-if="selectedViewType !== 'lifetime'">
         <button class="btn btn-outline-secondary me-1" @click="navigatePeriod(-1)" :disabled="loadingSummary || loadingActivities"><</button>
         <button class="btn btn-outline-secondary" @click="navigatePeriod(1)" :disabled="loadingSummary || loadingActivities">></button>
      </div>
    </div>

    <!-- Summary Display Section -->
    <div v-if="loadingSummary" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">{{ t('summaryView.loadingSummary') }}</span>
      </div>
    </div>
    <div v-else-if="summaryData" class="card mb-4">
      <div class="card-header">
        {{ summaryPeriodText }}
      </div>
      <div class="card-body">
        <!-- Display overall metrics -->
        <div class="row text-center mb-3">
           <div class="col"><strong>{{ t('summaryView.metricTotalDistance') }}:</strong><br>{{ formatDistance(summaryData.total_distance) }}</div>
           <div class="col"><strong>{{ t('summaryView.metricTotalDuration') }}:</strong><br>{{ formatDuration(summaryData.total_duration) }}</div>
           <div class="col"><strong>{{ t('summaryView.metricTotalElevation') }}:</strong><br>{{ formatElevation(summaryData.total_elevation_gain) }}</div>
           <div class="col"><strong>{{ t('summaryView.metricTotalCalories') }}:</strong><br>{{ formatCalories(summaryData.total_calories) }}</div>
           <div class="col"><strong>{{ t('summaryView.metricTotalActivities') }}:</strong><br>{{ summaryData.activity_count }}</div>
        </div>
        <hr>
        <!-- Display breakdown -->
        <h5>{{ t('summaryView.headerBreakdown') }}</h5>
        <div class="table-responsive">
          <table class="table table-sm table-striped">
            <thead>
              <tr>
                <th>{{ breakdownHeader }}</th>
                <th>{{ t('summaryView.colDistance') }}</th>
                <th>{{ t('summaryView.colDuration') }}</th>
                <th>{{ t('summaryView.colElevation') }}</th>
                <th>{{ t('summaryView.colCalories') }}</th>
                <th>{{ t('summaryView.colActivities') }}</th>
              </tr>
            </thead>
            <tbody>
               <tr v-for="item in summaryData.breakdown" :key="getBreakdownKey(item)">
                  <td>{{ getBreakdownLabel(item) }}</td>
                  <td>{{ formatDistance(item.total_distance) }}</td>
                  <td>{{ formatDuration(item.total_duration) }}</td>
                  <td>{{ formatElevation(item.total_elevation_gain) }}</td>
                  <td>{{ formatCalories(item.total_calories) }}</td>
                  <td>{{ item.activity_count }}</td>
               </tr>
               <tr v-if="!summaryData.breakdown || summaryData.breakdown.length === 0">
                  <td :colspan="6" class="text-center">{{ t('summaryView.noDataForPeriod') }}</td>
               </tr>
            </tbody>
          </table>
        </div>

        <!-- Type Breakdown Section - Only show if data exists AND no specific type is selected -->
        <div v-if="typeBreakdownData && !selectedActivityType" class="mt-4">
           <hr>
           <h5>{{ t('summaryView.headerTypeBreakdown') }}</h5>
           <div class="table-responsive">
             <table class="table table-sm table-striped">
               <thead>
                 <tr>
                   <th>{{ t('summaryView.colActivityType') }}</th>
                   <th>{{ t('summaryView.colDistance') }}</th>
                   <th>{{ t('summaryView.colDuration') }}</th>
                   <th>{{ t('summaryView.colElevation') }}</th>
                   <th>{{ t('summaryView.colCalories') }}</th>
                   <th>{{ t('summaryView.colActivities') }}</th>
                 </tr>
               </thead>
               <tbody>
                  <tr v-for="item in typeBreakdownData" :key="item.activity_type_id"> <!-- Use ID for key -->
                     <td class="text-center"><font-awesome-icon :icon="getIcon(item.activity_type_id)" /></td> <!-- Use ID for icon -->
                     <td>{{ formatDistance(item.total_distance) }}</td>
                     <td>{{ formatDuration(item.total_duration) }}</td>
                     <td>{{ formatElevation(item.total_elevation_gain) }}</td>
                     <td>{{ formatCalories(item.total_calories) }}</td>
                     <td>{{ item.activity_count }}</td>
                  </tr>
               </tbody>
             </table>
           </div>
        </div>
        <!-- End Type Breakdown Section -->

      </div>
    </div>
     <div v-else-if="errorSummary" class="alert alert-danger">
      {{ t('summaryView.errorLoadingSummary', { error: errorSummary }) }}
    </div>

    <!-- Activities List Section -->
    <div v-if="selectedViewType !== 'lifetime'">
      <h3 class="mt-4">{{ t('summaryView.headerActivitiesInPeriod') }}</h3>
      <div v-if="loadingActivities" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">{{ t('summaryView.loadingActivities') }}</span>
        </div>
      </div>
      <div v-else-if="errorActivities" class="alert alert-danger">
        {{ t('summaryView.errorLoadingActivities', { error: errorActivities }) }}
      </div>
      <div v-else>
        <ActivitiesTableComponent
          :activities="activities"
          :sort-by="sortBy"
          :sort-order="sortOrder"
          @sort-changed="handleSort"
        />
        <PaginationComponent
          v-if="totalActivities > 0"
          :current-page="currentPage"
          :total-pages="calculatedTotalPages"
          @page-changed="handlePageChange"
        />
        <p v-if="activities.length === 0 && !loadingActivities">{{ t('summaryView.noActivitiesFound') }}</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n'; // Import useI18n
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'; // Import FontAwesomeIcon
import { useAuthStore } from '@/stores/authStore';
import { summaryService } from '@/services/summaryService';
import { activities as activitiesService } from '@/services/activitiesService'; // Ensure this alias is used or adjust
import ActivitiesTableComponent from '@/components/Activities/ActivitiesTableComponent.vue';
import PaginationComponent from '@/components/Common/PaginationComponent.vue';
import { formatDistance, formatDuration, formatElevation, formatCalories, getIcon } from '@/utils/activityUtils'; // Import the icon utility
import {
  getWeekStartDate, getWeekEndDate, getMonthStartDate, getMonthEndDate, formatDateISO,
  parseMonthString, formatDateToMonthString // Removed unused week string functions
} from '@/utils/dateUtils';

const { t } = useI18n(); // Setup useI18n
const authStore = useAuthStore();

// Filter and View State
const selectedViewType = ref('week');
const selectedActivityType = ref(''); // Added for activity type filter, will hold the ID
const activityTypes = ref({}); // Changed to store {id: name} dictionary
const initialDate = new Date();
// selectedDate remains the canonical YYYY-MM-DD date used for fetching/calculations
const selectedDate = ref(formatDateISO(initialDate)); // Used for week view input and internal calculations
const selectedYear = ref(initialDate.getFullYear()); // Used for year view input
// selectedPeriodString holds the value ONLY for the month input field (YYYY-MM)
const selectedPeriodString = ref(formatDateToMonthString(initialDate)); // Initialize for month view

// Data State
const summaryData = ref(null);
const typeBreakdownData = ref(null); // Added ref for type breakdown
const activities = ref([]);
const totalActivities = ref(0);
const currentPage = ref(1);
const activitiesPerPage = ref(15);

// Loading and Error State
const loadingSummary = ref(false);
const errorSummary = ref(null);
const loadingActivities = ref(false);
const errorActivities = ref(null);
const loadingTypes = ref(false); // Added for type loading
const errorTypes = ref(null); // Added for type error

// Sorting State
const sortBy = ref('start_time');
const sortOrder = ref('desc');

// Computed property for dynamic input ID
const periodInputId = computed(() => {
  switch (selectedViewType.value) {
    case 'week': return 'periodPickerWeek';
    case 'month': return 'periodPickerMonth';
    case 'year': return 'periodPickerYear';
    default: return 'periodPicker'; // Fallback
  }
});

const periodLabel = computed(() => {
  switch (selectedViewType.value) {
    case 'week': return t('summaryView.labelSelectWeek');
    case 'month': return t('summaryView.labelSelectMonth');
    case 'year': return t('summaryView.labelSelectYear');
    case 'lifetime': return ''; // No label needed for lifetime
    default: return t('summaryView.labelSelectPeriod');
  }
})

const summaryPeriodText = computed(() => {
  if (!summaryData.value && !loadingSummary.value) return t('summaryView.labelSelectPeriod');
  if (loadingSummary.value) return t('summaryView.loading');

  try {
    if (selectedViewType.value === 'lifetime') {
      return t('summaryView.headerLifetimeTotals');
    }
    if (selectedViewType.value === 'year') {
      return t('summaryView.headerSummaryFor', { period: selectedYear.value });
    }
    // Use selectedDate for week and month views
    const date = new Date(selectedDate.value + 'T00:00:00Z'); // Use UTC
    if (isNaN(date.getTime())) return t('summaryView.invalidDateSelected');

    if (selectedViewType.value === 'month') {
      // Use Intl for month name formatting (respects locale)
      return t('summaryView.headerSummaryFor', { period: date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', timeZone: 'UTC' }) });
    }
    if (selectedViewType.value === 'week') {
      const weekStart = getWeekStartDate(date);
      // Keep simple for now, could translate "Week starting"
      return t('summaryView.headerSummaryFor', { period: `Week starting ${formatDateISO(weekStart)}` });
    }
  } catch (e) {
    console.error("Error formatting summary period text:", e);
    return t('summaryView.labelSelectPeriod'); // Fallback
  }
  return '';
})

const breakdownHeader = computed(() => {
  switch (selectedViewType.value) {
    case 'week': return t('summaryView.colDay');
    case 'month': return t('summaryView.colWeekNum');
    case 'year': return t('summaryView.colMonth');
    case 'lifetime': return t('summaryView.colYear');
    default: return 'Period'; // Fallback, should not happen
  }
})

const getBreakdownKey = (item) => {
  switch (selectedViewType.value) {
    case 'week': return item.day_of_week;
    case 'month': return item.week_number;
    case 'year': return item.month_number;
    case 'lifetime': return item.year;
    default: return '';
  }
}

const getBreakdownLabel = (item) => {
   switch (selectedViewType.value) {
    case 'week':
        // Use Intl for weekday names (respects locale and start day)
        const tempDate = new Date(); // Create a date object
        // Find a date that corresponds to the day_of_week (0=Mon, 6=Sun)
        // Note: This assumes ISO 8601 week date system (Monday=1, Sunday=7) used by backend 'isodow'
        // Adjusting to match JavaScript's getUTCDay (Sunday=0, Saturday=6) might be complex.
        // For simplicity, using fixed English names for now. Consider a more robust locale-aware solution later.
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        return days[item.day_of_week] || 'Unknown Day';
    case 'month':
        return `${t('summaryView.colWeekNum')} ${item.week_number}`; // Translate "Week #"
    case 'year':
        // Use Intl for month names
        const monthDate = new Date(Date.UTC(selectedYear.value, item.month_number - 1, 1));
        return monthDate.toLocaleDateString(undefined, { month: 'long', timeZone: 'UTC' });
    case 'lifetime':
        return item.year;
    default: return '';
  }
}

// Fetch available activity types for the filter dropdown
const fetchActivityTypes = async () => {
  if (!authStore.user?.id) return;
  loadingTypes.value = true;
  errorTypes.value = null;
  try {
    // Store the dictionary directly
    activityTypes.value = await activitiesService.getActivityTypes();
  } catch (err) {
    console.error('Failed to fetch activity types:', err);
    errorTypes.value = t('generalItems.labelError'); // Use a generic error message
  } finally {
    loadingTypes.value = false;
  }
};

const fetchSummaryData = async () => {
  if (!authStore.user?.id) return;

  loadingSummary.value = true
  errorSummary.value = null
  summaryData.value = null
  typeBreakdownData.value = null // Reset type breakdown
  
  // Reset activities only if not in lifetime view, or if it's the first page of lifetime view
  if (selectedViewType.value !== 'lifetime') {
    activities.value = []
    totalActivities.value = 0
    currentPage.value = 1
  }


  try {
    const params = {};
    if (selectedViewType.value === 'year') {
      if (!selectedYear.value || selectedYear.value < 1900 || selectedYear.value > 2100) {
         throw new Error(t('summaryView.invalidYearSelected'));
      }
      params.year = selectedYear.value;
    } else if (selectedViewType.value === 'week' || selectedViewType.value === 'month') {
       if (!selectedDate.value) {
          throw new Error(t('summaryView.noDateSelected'));
       }
      // Always use selectedDate for week/month API calls
      params.date = selectedDate.value;
    } // No params for 'lifetime' view type for date/year

    // Look up the activity type name from the ID for the summary service
    const activityTypeName = selectedActivityType.value ? activityTypes.value[selectedActivityType.value] : null;

    // Pass the selected activity type NAME to the summary service call
    const response = await summaryService.getSummary(
        authStore.user.id,
        selectedViewType.value,
        params,
        activityTypeName // Pass selected type NAME or null
    );
    summaryData.value = response; // Assign the main summary data
    typeBreakdownData.value = response.type_breakdown; // Assign the type breakdown data
    
    if (selectedViewType.value !== 'lifetime') {
      fetchActivitiesForPeriod(); // Fetch activities *after* summary is loaded for non-lifetime views
    } else {
      // For lifetime view, clear activities as they are not displayed
      activities.value = [];
      totalActivities.value = 0;
      currentPage.value = 1;
      loadingActivities.value = false; // Ensure loading state is reset
      errorActivities.value = null; // Ensure error state is reset
    }
  } catch (err) {
    console.error('Error fetching summary:', err)
    // Use error message from exception if available, otherwise use generic translated message
    errorSummary.value = err.message || (err.response?.data?.detail || t('generalItems.labelError'))
  } finally {
    loadingSummary.value = false
  }
}

const fetchActivitiesForPeriod = async (page = currentPage.value) => {
   if (!authStore.user?.id) return

   loadingActivities.value = true
   errorActivities.value = null
   if (page === 1) {
       activities.value = []
       totalActivities.value = 0
   }

   try {
     let startDateStr, endDateStr

     if (selectedViewType.value === 'year') {
        startDateStr = `${selectedYear.value}-01-01`
        endDateStr = `${selectedYear.value + 1}-01-01`
     } else {
        // Use selectedDate for week/month start/end calculations
        const date = new Date(selectedDate.value + 'T00:00:00Z')
        if (isNaN(date.getTime())) throw new Error(t('summaryView.invalidDateSelected'));

        if (selectedViewType.value === 'week') {
            const weekStart = getWeekStartDate(date)
            const weekEnd = getWeekEndDate(date)
            startDateStr = formatDateISO(weekStart)
            endDateStr = formatDateISO(weekEnd)
        } else { // month
            const monthStart = getMonthStartDate(date)
            const monthEnd = getMonthEndDate(date)
            startDateStr = formatDateISO(monthStart)
            endDateStr = formatDateISO(monthEnd)
        }
     }

     // Prepare filters, including the new activity type filter
     const filters = {
       start_date: startDateStr,
       end_date: endDateStr,
       type: selectedActivityType.value || null // Pass null or omit if empty string
     };
     // Remove null/empty filters
     Object.keys(filters).forEach(key => (filters[key] == null || filters[key] === '') && delete filters[key]);


     const response = await activitiesService.getUserActivitiesWithPagination(
         authStore.user.id,
         page,
         activitiesPerPage.value,
         filters, // Pass the filters object
         sortBy.value, // Pass sort column
         sortOrder.value // Pass sort order
     );

     activities.value = response.activities || []
     totalActivities.value = response.total_count || 0
     currentPage.value = page

   } catch (err) {
     console.error('Error fetching activities:', err)
     errorActivities.value = err.message || (err.response?.data?.detail || t('generalItems.labelError'))
   } finally {
     loadingActivities.value = false
   }
}

// Function to handle page changes from pagination component
function handlePageChange(newPage) {
  fetchActivitiesForPeriod(newPage)
}

// Function to handle sorting changes from table component
function handleSort(columnName) {
  if (sortBy.value === columnName) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = columnName
    sortOrder.value = 'desc'
  }
  fetchActivitiesForPeriod(1);
}

// Function to handle triggering data fetch when relevant period changes
function triggerDataFetch() {
    currentPage.value = 1;
    // Ensure selectedDate/selectedYear is valid before fetching
    if (
        (selectedViewType.value === 'week' && selectedDate.value) ||
        (selectedViewType.value === 'month' && selectedDate.value) || // selectedPeriodString updates selectedDate
        (selectedViewType.value === 'year' && selectedYear.value) ||
        selectedViewType.value === 'lifetime' // Always fetch for lifetime
    ) {
        fetchSummaryData();
    } else {
        console.warn("Skipping fetch, invalid date or year for current view type.");
        // Optionally clear data or show a message
        summaryData.value = null;
        typeBreakdownData.value = null;
        activities.value = [];
        totalActivities.value = 0;
        errorSummary.value = t('summaryView.noDateSelected'); // Or a more specific error
    }
}

// Handler for the date input change (used in week view)
function handleDateInputChange() {
    // The v-model already updated selectedDate, just trigger the fetch
    triggerDataFetch();
}

// Watch for changes in the selected period string (month input ONLY)
watch(selectedPeriodString, (newString) => {
  // Only act if in month view and the string is valid
  if (selectedViewType.value !== 'month' || !newString) return;
  try {
    const newDate = parseMonthString(newString); // Gets the 1st of the month
    if (newDate && !isNaN(newDate.getTime())) {
      const newDateISO = formatDateISO(newDate);
      // Update selectedDate only if it differs, to avoid redundant fetches
      if (newDateISO !== selectedDate.value) {
        selectedDate.value = newDateISO;
        triggerDataFetch(); // Fetch data for the new month
      }
    }
  } catch (e) {
    console.error(`Error parsing month string ${newString}:`, e);
    errorSummary.value = t('summaryView.invalidInputFormat');
  }
});

// Watch for changes in the selected year input
watch(selectedYear, (newYear) => {
    // Only act if in year view and the year is valid
    if (selectedViewType.value !== 'year' || !newYear) return;
    // Basic validation, could be more robust
    if (newYear >= 1900 && newYear <= 2100) {
         triggerDataFetch(); // Fetch data for the new year
    } else {
        console.warn("Invalid year selected:", newYear);
        errorSummary.value = t('summaryView.invalidYearSelected');
        // Clear data as the year is invalid
        summaryData.value = null;
        typeBreakdownData.value = null;
        activities.value = [];
        totalActivities.value = 0;
    }
});

// Watch for changes in the activity type filter dropdown
watch(selectedActivityType, () => {
  // When the type filter changes, refetch data starting from page 1
  triggerDataFetch();
});

// Watch for changes in the view type dropdown
watch(selectedViewType, (newType) => {
  try {
    // Ensure selectedDate is valid before proceeding, reset if not
    let baseDate;
    try {
        baseDate = new Date(selectedDate.value + 'T00:00:00Z');
        if (isNaN(baseDate.getTime())) throw new Error("Invalid base date");
    } catch {
        baseDate = new Date(); // Default to today if selectedDate was invalid
        selectedDate.value = formatDateISO(baseDate);
    }

    // Update the relevant input model based on the new view type
    if (newType === 'month') {
      selectedPeriodString.value = formatDateToMonthString(baseDate);
    } else if (newType === 'year') {
      selectedYear.value = baseDate.getUTCFullYear();
    }
    // No explicit update needed for 'week' as selectedDate is already the model

    // Trigger data fetch for the new view type and period
    triggerDataFetch();

  } catch (e) {
      console.error("Error handling view type change:", e);
      errorSummary.value = t('generalItems.labelError');
      // Attempt to reset to a known state (e.g., weekly view with today's date)
      const today = new Date();
      selectedViewType.value = 'week'; // Reset view type
      selectedDate.value = formatDateISO(today);
      triggerDataFetch(); // Attempt fetch with reset state
  }
});

// Function to navigate period back/forward
function navigatePeriod(direction) {
    try {
        if (selectedViewType.value === 'year') {
            selectedYear.value += direction;
            // Watcher on selectedYear will trigger data fetch
        } else {
            const currentDate = new Date(selectedDate.value + 'T00:00:00Z');
            if (isNaN(currentDate.getTime())) return; // Should not happen

            if (selectedViewType.value === 'week') {
                currentDate.setUTCDate(currentDate.getUTCDate() + (7 * direction));
                selectedDate.value = formatDateISO(currentDate); // Update date input model
                triggerDataFetch(); // Manually trigger fetch for week navigation
            } else { // month
                currentDate.setUTCMonth(currentDate.getUTCMonth() + direction);
                // Update the month input model; watcher will handle the rest
                selectedPeriodString.value = formatDateToMonthString(currentDate);
            }
        }
    } catch (e) {
        console.error("Error navigating period:", e);
        errorSummary.value = t('generalItems.labelError'); // Show generic error
    }
}

// Calculate total pages for pagination
const calculatedTotalPages = computed(() => {
  return totalActivities.value > 0 ? Math.ceil(totalActivities.value / activitiesPerPage.value) : 1
})

// Fetch initial data on component mount
onMounted(() => {
  fetchActivityTypes(); // Fetch types first
  triggerDataFetch(); // Then fetch summary and activities based on initial state
});

</script>

<style scoped>
.table-responsive {
    max-height: 400px; /* Example height for scrollable breakdown */
}
.card .row.text-center p {
    margin-bottom: 0;
}
/* Ensure buttons align nicely */
.align-items-end {
    align-items: flex-end;
}
</style>
