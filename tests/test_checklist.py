import pytest

from features.checklist import GEAR_CATALOG, export_markdown


REQUIRED_GROUPS = {
    "Shelter",
    "Sleeping",
    "Food and water",
    "Safety",
    "Clothing",
    "Responsible travel / Leave No Trace",
}


def test_catalog_covers_each_activity_and_required_group():
    assert set(GEAR_CATALOG) == {"Hiking", "Camping", "Trekking", "Sightseeing"}

    for groups in GEAR_CATALOG.values():
        assert set(groups) == REQUIRED_GROUPS
        items = [item for group_items in groups.values() for item in group_items]
        assert items
        assert all(item["name"] and item["id"] for item in items)
        assert all(item["priority"] in {"essential", "optional"} for item in items)
        assert any(
            item["priority"] == "essential" for item in items
        )
        assert any(
            item["priority"] == "optional" for item in items
        )
        assert any(
            "Leave No Trace" in group for group in groups
        )


def test_export_marks_checked_items_and_groups_essentials_and_optionals():
    first_essential = next(
        item
        for items in GEAR_CATALOG["Hiking"].values()
        for item in items
        if item["priority"] == "essential"
    )
    markdown = export_markdown("Hiking", {first_essential["id"]})

    assert "# Hiking Gear Checklist" in markdown
    assert "## Essential items" in markdown
    assert "## Optional items" in markdown
    assert f"- [x] {first_essential['name']}" in markdown
    assert "## Responsible travel / Leave No Trace" in markdown
    assert markdown.endswith("\n")


def test_export_rejects_unknown_activity():
    with pytest.raises(ValueError, match="Unknown activity"):
        export_markdown("Climbing")
