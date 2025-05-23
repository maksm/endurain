<template>
    <!-- Modal add/edit weight -->
    <div class="modal fade" :id="action == 'add' ? 'addWeightModal' : (action == 'edit' ? editWeightId : '')" tabindex="-1" :aria-labelledby="action == 'add' ? 'addWeightModal' : (action == 'edit' ? editWeightId : '')" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="addWeightModal" v-if="action == 'add'">{{ $t("healthWeightAddEditModalComponent.addWeightModalTitle") }}</h1>
					<h1 class="modal-title fs-5" :id="editWeightId" v-else>{{ $t("healthWeightAddEditModalComponent.editWeightModalTitle") }}</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <form  @submit.prevent="handleSubmit">
                    <div class="modal-body">
                        <!-- weight fields -->
                        <label for="weightWeightAdd"><b>* {{ $t("healthWeightAddEditModalComponent.addWeightWeightLabel") }}</b></label>
                        <input class="form-control" type="number" step="0.1" name="weightWeightAdd" v-model="newEditWeightWeight" required>
                        <!-- date fields -->
                        <label for="weightDateAdd"><b>* {{ $t("healthWeightAddEditModalComponent.addWeightDateLabel") }}</b></label>
                        <input class="form-control" type="date" name="weightDateAdd" v-model="newEditWeightDate" required>
                        
                        <p>* {{ $t("generalItems.requiredField") }}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            {{ $t("generalItems.buttonClose") }}
                        </button>
                        <button type="submit" class="btn btn-success" data-bs-dismiss="modal" v-if="action == 'add'">
                            {{ $t("healthWeightAddEditModalComponent.addWeightModalTitle") }}
                        </button>
						<button type="submit" class="btn btn-success" data-bs-dismiss="modal" v-else>
							{{ $t("healthWeightAddEditModalComponent.editWeightModalTitle") }}
						</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { ref } from "vue";
import { useI18n } from "vue-i18n";
// Import Notivue push
import { push } from "notivue";
// Importing the services
import { health_data } from "@/services/health_dataService";
// Import the stores
import { useAuthStore } from "@/stores/authStore";
// Importing the utils
import { lbsToKg, kgToLbs } from "@/utils/unitsUtils";

export default {
    props: {
		action: {
			type: String,
			required: true,
		},
		data: {
			type: Object,
			required: false,
		},
	},
    emits: ["isLoadingNewWeight", "createdWeight", "editedWeight"],
	setup(props, { emit }) {
		const authStore = useAuthStore();
		const { t } = useI18n();
		const newEditWeightWeight = ref(50);
		const newEditWeightDate = ref(new Date().toISOString().split('T')[0]);
        const editWeightId = ref("");

        if(props.data){
            newEditWeightWeight.value = Number(authStore?.user?.units) === 1 ? props.data.weight : kgToLbs(props.data.weight);
            newEditWeightDate.value = props.data.date;
            editWeightId.value = `editWeightId${props.data.id}`;
        }

        async function submitAddWeight(){
			// Set the loading variable to true.
            emit("isLoadingNewWeight", true);
			try {
                // Create the weight data object.
                const data = {
                    weight: Number(authStore?.user?.units) === 1 ? newEditWeightWeight.value : lbsToKg(newEditWeightWeight.value),
                    date: newEditWeightDate.value,
                };

                const createdWeight = await health_data.createHealthData(data);

                // Set the loading variable to false.
                emit("isLoadingNewWeight", false);

                // Get the created weight and emit it
                emit("createdWeight", createdWeight);

                push.success(t("healthWeightAddEditModalComponent.successAddWeight"));
            } catch (error) {
				// If there is an error, show toast with error message
				// Set the loading variable to false.
				emit("isLoadingNewWeight", false);
                push.error(`${t("healthWeightAddEditModalComponent.errorAddWeight")} - ${error.toString()}`);
			}
        }

        function submitEditWeight(){
            emit("editedWeight", {
				id: props.data.id,
                user_id: props.data.user_id,
				weight: newEditWeightWeight.value,
                date: newEditWeightDate.value,
			});
        }

        function handleSubmit() {
            if (props.action === 'add') {
                submitAddWeight();
            } else {
                submitEditWeight();
            }
        }

        return {
    	    newEditWeightWeight,
            newEditWeightDate,
            editWeightId,
            handleSubmit,
		};
	},
};

</script>