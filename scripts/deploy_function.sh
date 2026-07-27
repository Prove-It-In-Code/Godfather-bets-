#!/usr/bin/env bash
set -euo pipefail

: "${RESOURCE_GROUP:?Set RESOURCE_GROUP}"
: "${LOCATION:?Set LOCATION (e.g. eastus)}"
: "${STORAGE_ACCOUNT:?Set STORAGE_ACCOUNT (globally unique)}"
: "${FUNCTION_APP:?Set FUNCTION_APP (globally unique)}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az storage account create --name "$STORAGE_ACCOUNT" --location "$LOCATION" --resource-group "$RESOURCE_GROUP" --sku Standard_LRS
az functionapp create --resource-group "$RESOURCE_GROUP" --consumption-plan-location "$LOCATION" --runtime python --runtime-version 3.11 --functions-version 4 --name "$FUNCTION_APP" --storage-account "$STORAGE_ACCOUNT"
func azure functionapp publish "$FUNCTION_APP" --python
