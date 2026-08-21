

from models.variant import Variant
from models.standard_navigation import StandardNavigation
from models.connected_navigation import ConnectedNavigation

def create_navigation_app(variant_type):
    if variant_type == Variant.VARIANT_A:
       connected_navigation_data = ConnectedNavigation(navigation_data="Connected Map Data")
       return connected_navigation_data
    else:
       standard_navigation_data = StandardNavigation(map_data="Standard Map Data", name="Standard Navigation", description="Basic navigation system")
       return standard_navigation_data

if __name__ == "__main__":
    # Example usage
    variant = Variant.VARIANT_A  # Change this to test different variants
    navigation_app = create_navigation_app(variant)

    # Test the navigation app
    route = navigation_app.calculate_route("Point A", "Point B")
    current_location = navigation_app.get_current_location()
    navigation_app.update_map("Updated Map Data")

    print(f"Route: {route}")
    print(f"Current Location: {current_location}")