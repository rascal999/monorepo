import { call, put, takeLatest } from 'redux-saga/effects';
import { fetchModels } from '../../services/openRouterApi';
import { fetchModelsStart, fetchModelsSuccess, fetchModelsFailure } from '../slices/uiSlice';
import type { AIModel } from '../slices/uiSlice';

function* fetchModelsSaga() {
  try {
    const models: AIModel[] = yield call(fetchModels);
    yield put(fetchModelsSuccess(models));
  } catch (error) {
    yield put(fetchModelsFailure(error instanceof Error ? error.message : 'Failed to fetch models'));
  }
}

export function* modelsSaga() {
  yield takeLatest(fetchModelsStart.type, fetchModelsSaga);
}
