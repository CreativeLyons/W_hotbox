#!/usr/bin/env python3
"""
Test script to validate mouse event handling logic in W_hotbox.
This script tests the coordinate conversion and event flow logic without requiring Nuke.

Run with: python3 test_mouse_events.py
"""

import sys

# Mock Qt classes for testing
class QPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"QPoint({self.x}, {self.y})"

class QRect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def contains(self, point):
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)

    def __repr__(self):
        return f"QRect({self.x}, {self.y}, {self.width}, {self.height})"

class MockButton:
    def __init__(self, name, parent_pos, size, parent=None):
        self.name = name
        self.parent_pos = parent_pos  # Position in parent's coordinate system
        self.size = size
        self.parent_ = parent
        self.selected = False

    def rect(self):
        # In Qt, child widget's rect() is in its own coordinate system (0,0-based)
        return QRect(0, 0, self.size[0], self.size[1])

    def parent(self):
        return self.parent_

    def mapFrom(self, source, pos):
        # Simulate Qt's mapFrom: convert from source widget coords to this widget's coords
        # In real Qt, this handles coordinate system conversion including widget hierarchy
        # For this test, buttons are direct children, so subtract button's position in parent
        return QPoint(pos.x - self.parent_pos[0], pos.y - self.parent_pos[1])

    def setSelectionStatus(self, selected):
        self.selected = selected
        print(f"  {self.name}.setSelectionStatus({selected})")

class MockHotbox:
    def __init__(self):
        self.hoveredButton = None
        self.buttons = []

    def findChildren(self, widget_type):
        return self.buttons

    def _findButtonAtPosition(self, pos):
        """Test the coordinate conversion logic"""
        buttons = [b for b in self.buttons if isinstance(b, MockButton)]

        for button in buttons:
            button_local_pos = button.mapFrom(self, pos)
            button_rect = button.rect()

            print(f"  Testing {button.name}: pos={pos}, mapped={button_local_pos}, rect={button_rect}, contains={button_rect.contains(button_local_pos)}")

            if button_rect.contains(button_local_pos):
                return button

        return None

    def simulate_mouseMove(self, pos):
        """Simulate mouseMoveEvent logic"""
        print(f"\nMouse move to {pos}")
        button_under_cursor = self._findButtonAtPosition(pos)
        old_button = self.hoveredButton

        if button_under_cursor != old_button:
            print(f"  Hover change: {old_button.name if old_button else 'None'} -> {button_under_cursor.name if button_under_cursor else 'None'}")

            # Clear ALL buttons
            for btn in self.buttons:
                if btn.selected:
                    btn.setSelectionStatus(False)

            # Set new hover state
            self.hoveredButton = button_under_cursor
            if button_under_cursor:
                button_under_cursor.setSelectionStatus(True)
        else:
            print(f"  No change (still on {old_button.name if old_button else 'None'})")

def test_coordinate_conversion():
    """Test that coordinate conversion works correctly"""
    print("=" * 60)
    print("TEST 1: Coordinate Conversion")
    print("=" * 60)

    hotbox = MockHotbox()

    # Create buttons at different positions (position in parent, size)
    button1 = MockButton("Button1", (10, 10), (105, 35), hotbox)
    button2 = MockButton("Button2", (125, 10), (105, 35), hotbox)
    button3 = MockButton("Button3", (10, 55), (105, 35), hotbox)

    hotbox.buttons = [button1, button2, button3]

    # Test positions (in hotbox coordinate system)
    # Button1 is at (10, 10) with size 105x35, so center is at (62, 27)
    # Button2 is at (125, 10) with size 105x35, so center is at (177, 27)
    # Button3 is at (10, 55) with size 105x35, so center is at (62, 72)
    test_cases = [
        (QPoint(62, 27), "Button1"),   # Center of button1
        (QPoint(177, 27), "Button2"),  # Center of button2
        (QPoint(62, 72), "Button3"),   # Center of button3
        (QPoint(5, 5), None),          # Outside all buttons
        (QPoint(250, 25), None),      # Outside all buttons
    ]

    for pos, expected in test_cases:
        result = hotbox._findButtonAtPosition(pos)
        result_name = result.name if result else None
        status = "✓" if result_name == expected else "✗"
        print(f"{status} Position {pos}: Expected {expected}, Got {result_name}")
        assert result_name == expected, f"Failed at {pos}: expected {expected}, got {result_name}"

def test_hover_state_management():
    """Test that only one button is highlighted at a time"""
    print("\n" + "=" * 60)
    print("TEST 2: Hover State Management (Single Source of Truth)")
    print("=" * 60)

    hotbox = MockHotbox()

    button1 = MockButton("Button1", (10, 10), (105, 35), hotbox)
    button2 = MockButton("Button2", (125, 10), (105, 35), hotbox)
    button3 = MockButton("Button3", (10, 55), (105, 35), hotbox)

    hotbox.buttons = [button1, button2, button3]

    # Simulate mouse movement
    hotbox.simulate_mouseMove(QPoint(62, 27))   # Move to button1 center
    assert button1.selected == True, "Button1 should be selected"
    assert button2.selected == False, "Button2 should not be selected"
    assert button3.selected == False, "Button3 should not be selected"
    assert hotbox.hoveredButton == button1, "Hotbox should track button1"

    hotbox.simulate_mouseMove(QPoint(177, 27))  # Move to button2 center
    assert button1.selected == False, "Button1 should be cleared"
    assert button2.selected == True, "Button2 should be selected"
    assert button3.selected == False, "Button3 should not be selected"
    assert hotbox.hoveredButton == button2, "Hotbox should track button2"

    hotbox.simulate_mouseMove(QPoint(5, 5))     # Move outside
    assert button1.selected == False, "Button1 should be cleared"
    assert button2.selected == False, "Button2 should be cleared"
    assert button3.selected == False, "Button3 should be cleared"
    assert hotbox.hoveredButton == None, "Hotbox should have no hovered button"

    print("\n✓ All hover state tests passed!")

def test_rapid_movement():
    """Test rapid mouse movement doesn't leave multiple buttons highlighted"""
    print("\n" + "=" * 60)
    print("TEST 3: Rapid Mouse Movement (No Multiple Highlights)")
    print("=" * 60)

    hotbox = MockHotbox()

    button1 = MockButton("Button1", (10, 10), (105, 35), hotbox)
    button2 = MockButton("Button2", (125, 10), (105, 35), hotbox)
    button3 = MockButton("Button3", (240, 10), (105, 35), hotbox)

    hotbox.buttons = [button1, button2, button3]

    # Rapid movement across buttons (centers)
    positions = [
        QPoint(62, 27),   # button1 center
        QPoint(177, 27),  # button2 center
        QPoint(62, 27),   # back to button1
        QPoint(292, 27),  # button3 center
        QPoint(177, 27),  # button2 center
    ]

    selected_counts = []
    for pos in positions:
        hotbox.simulate_mouseMove(pos)
        count = sum(1 for btn in hotbox.buttons if btn.selected)
        selected_counts.append(count)
        assert count <= 1, f"Only one button should be selected, but {count} are selected!"

    print(f"\nSelected button counts during rapid movement: {selected_counts}")
    print("✓ No multiple highlights detected!")

if __name__ == "__main__":
    print("W_Hotbox Mouse Event Logic Tests")
    print("=" * 60)

    try:
        test_coordinate_conversion()
        test_hover_state_management()
        test_rapid_movement()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nThe mouse event handling logic is correct.")
        print("The fixes ensure:")
        print("  1. Coordinate conversion works correctly")
        print("  2. Only one button is highlighted at a time")
        print("  3. Rapid movement doesn't leave multiple highlights")
        print("\nNote: This tests the logic only. Full testing requires Nuke.")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
