

class Spaceship:
    def __init__(self, coordinates, description, health, heading, speed, maneuverability, firepower, stealth, defense, warp_capacity):
        self.coordinates = coordinates  # A tuple of (x, y, z)
        self.description = description
        self.health = health
        self.heading = heading  # Destination coordinates
        self.speed = speed

        # Ship capabilities
        self.maneuverability = maneuverability # Ability to dodge or outmaneuver other ships
        self.firepower = firepower  # Damage the ship can deal
        self.stealth = stealth  # Ability to avoid detection
        self.defense = defense  # Resistance to damage
        self.warp_capacity = warp_capacity  # Ability to travel at faster-than-light speeds
        
        # Roles available in the spaceship and their current occupant
        self.roles = {
            'navigator': None,
            'engineer': None,
            'weapons_officer': None,
            'pilot': None
        }
        
    def set_role(self, role, crew_member):
        """Assign a crew member to a role."""
        if role in self.roles:
            self.roles[role] = crew_member
        else:
            raise ValueError(f"{role} is not a valid role on this spaceship.")
            
    def get_role(self, role):
        """Get the crew member currently occupying a role."""
        if role in self.roles:
            return self.roles[role]
        else:
            raise ValueError(f"{role} is not a valid role on this spaceship.")
    
    def status(self):
        """Print out the current status of the spaceship."""
        print(f"Spaceship {self.description} currently at coordinates {self.coordinates}.")
        print(f"Health: {self.health}, Heading: {self.heading}, Speed: {self.speed}, Maneuverability: {self.maneuverability}")
        print(f"Firepower: {self.firepower}, Stealth: {self.stealth}, Defense: {self.defense}, Warp Capacity: {self.warp_capacity}")
        for role, member in self.roles.items():
            print(f"{role.title()}: {member if member else 'Unoccupied'}")
