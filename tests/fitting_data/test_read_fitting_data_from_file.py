from collections import OrderedDict, namedtuple
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from mock import Mock, PropertyMock, mock_open, patch
from pytest_cases import fixture_ref, parametrize

from eddington import FittingData, FittingDataInvalidFileSyntax
from tests.fitting_data import COLUMNS, CONTENT, ROWS, VALUES

DummyCell = namedtuple("DummyCell", "value")
FILENAME = "file"
FILE_PATH = Path("path/to") / FILENAME
SHEET_NAME = "sheet"


def check_data_by_keys(actual_fitting_data):
    for key in actual_fitting_data.data.keys():
        np.testing.assert_equal(
            actual_fitting_data.data[key],
            COLUMNS[key],
            err_msg="Data is different than expected",
        )


def check_data_by_indexes(actual_fitting_data):
    for key in actual_fitting_data.data.keys():
        np.testing.assert_equal(
            actual_fitting_data.data[key],
            VALUES[int(key)],
            err_msg="Data is different than expected",
        )


def check_columns(
    actual_fitting_data, x_column=0, xerr_column=1, y_column=2, yerr_column=3
):
    np.testing.assert_equal(
        actual_fitting_data.x,
        VALUES[x_column],
        err_msg="X is different than expected",
    )
    np.testing.assert_equal(
        actual_fitting_data.xerr,
        VALUES[xerr_column],
        err_msg="X Error is different than expected",
    )
    np.testing.assert_equal(
        actual_fitting_data.y,
        VALUES[y_column],
        err_msg="Y is different than expected",
    )
    np.testing.assert_equal(
        actual_fitting_data.yerr,
        VALUES[yerr_column],
        err_msg="Y Error is different than expected",
    )


def set_csv_rows(reader, rows):
    reader.return_value = rows


@pytest.fixture
def read_csv(mocker):
    reader = mocker.patch("csv.reader")
    m_open = mock_open()

    def actual_read(file_path, **kwargs):
        with patch("eddington.fitting_data.open", m_open):
            actual_fitting_data = FittingData.read_from_csv(file_path, **kwargs)
        return actual_fitting_data

    return actual_read, dict(reader=reader, row_setter=set_csv_rows)


def set_excel_rows(reader, rows):
    sheet = Mock()
    reader.return_value = {SHEET_NAME: sheet}
    type(sheet).values = PropertyMock(return_value=rows)


@pytest.fixture
def read_excel(mock_load_workbook):
    def actual_read(file_path, **kwargs):
        return FittingData.read_from_excel(file_path, SHEET_NAME, **kwargs)

    return actual_read, dict(reader=mock_load_workbook, row_setter=set_excel_rows)


def set_json_rows(reader, rows):
    reader.return_value = OrderedDict(zip(rows[0], zip(*rows[1:])))


@pytest.fixture
def read_json(mock_load_json):
    m_open = mock_open()

    def actual_read(file_path, **kwargs):
        with patch("eddington.fitting_data.open", m_open):
            return FittingData.read_from_json(file_path, **kwargs)

    return actual_read, dict(reader=mock_load_json, row_setter=set_json_rows)


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_headers_successful(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(FILE_PATH)

    check_data_by_keys(actual_fitting_data)
    check_columns(actual_fitting_data)


@parametrize("read, mocks", [fixture_ref(read_csv), fixture_ref(read_excel)])
def test_read_without_headers_successful(read, mocks):
    mocks["row_setter"](mocks["reader"], CONTENT)
    actual_fitting_data = read(FILE_PATH)
    check_data_by_indexes(actual_fitting_data)
    check_columns(actual_fitting_data)


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_invalid_string_in_row(read, mocks):
    rows = deepcopy(ROWS)
    rows[1][0] = "f"
    mocks["row_setter"](mocks["reader"], rows)

    with pytest.raises(FittingDataInvalidFileSyntax):
        read(FILE_PATH)


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_none_in_row(read, mocks):
    rows = deepcopy(ROWS)
    rows[1][0] = None
    mocks["row_setter"](mocks["reader"], rows)

    with pytest.raises(FittingDataInvalidFileSyntax):
        read(FILE_PATH)


@parametrize("read, mocks", [fixture_ref(read_csv), fixture_ref(read_excel)])
def test_read_with_empty_header(read, mocks):
    rows = deepcopy(ROWS)
    rows[0][0] = ""
    mocks["row_setter"](mocks["reader"], rows)

    with pytest.raises(FittingDataInvalidFileSyntax):
        read(FILE_PATH)


@parametrize("read, mocks", [fixture_ref(read_csv), fixture_ref(read_excel)])
def test_read_with_float_header(read, mocks):
    rows = deepcopy(ROWS)
    rows[0][0] = "1.25"
    mocks["row_setter"](mocks["reader"], rows)

    with pytest.raises(FittingDataInvalidFileSyntax):
        read(FILE_PATH)


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_x_column(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(FILE_PATH, x_column=3)

    check_columns(
        actual_fitting_data, x_column=2, xerr_column=3, y_column=4, yerr_column=5
    )


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_xerr_column(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(FILE_PATH, xerr_column=3)

    check_columns(
        actual_fitting_data, x_column=0, xerr_column=2, y_column=3, yerr_column=4
    )


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_y_column(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(FILE_PATH, y_column=5)

    check_columns(
        actual_fitting_data, x_column=0, xerr_column=1, y_column=4, yerr_column=5
    )


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_with_yerr_column(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(FILE_PATH, yerr_column=5)

    check_columns(
        actual_fitting_data, x_column=0, xerr_column=1, y_column=2, yerr_column=4
    )


@parametrize(
    "read, mocks",
    [fixture_ref(read_csv), fixture_ref(read_excel), fixture_ref(read_json)],
)
def test_read_string_path_successful(read, mocks):
    mocks["row_setter"](mocks["reader"], ROWS)

    actual_fitting_data = read(str(FILE_PATH))

    check_data_by_keys(actual_fitting_data)
    check_columns(actual_fitting_data)
