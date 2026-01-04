from datetime import datetime, timedelta

class Movie:
    def __init__(self, movie_id, title, duration_minutes, rating, genre, actors=None):
        self.movie_id = movie_id
        self.title = title  
        self.duration_minutes = duration_minutes  
        self.rating = rating
        self.genre = genre
        self.actors = actors or []

    def __str__(self):
        return f"Movie: {self.title} ({self.duration_minutes} min), Genre: {self.genre}, Rating: {self.rating}"

# ---

class Seat:
    def __init__(self, seat_id, row, number, price_category="Standard"):
        self.seat_id = seat_id 
        self.row = row          
        self.number = number    
        self.price_category = price_category 
        self.is_reserved = False 

    def __str__(self):
        status = "RESERVED" if self.is_reserved else "AVAILABLE"
        return f"Seat: {self.row}{self.number} ({self.price_category}), Status: {status}"
        
# ---

class Theater:
    def __init__(self, theater_id, name, rows=8, seats_per_row=10):
        self.theater_id = theater_id
        self.name = name  
        self.rows = rows
        self.seats_per_row = seats_per_row
        self.seats = {} 
        self._generate_seats()

    def _generate_seats(self):
        """Auto-generate seats"""
        seat_id = 1
        for row_idx in range(self.rows):
            row_letter = chr(65 + row_idx)  # A, B, C...
            for seat_num in range(1, self.seats_per_row + 1):
                # Middle seats are VIP
                category = "VIP" if row_idx in [3, 4] and 3 <= seat_num <= 8 else "Standard"
                seat = Seat(seat_id, row_letter, seat_num, category)
                self.seats[seat_id] = seat
                seat_id += 1

    def render_seat_map(self):
        """Display seat map visually"""
        print(f"\n{'='*50}")
        print(f"  {self.name} - Seat Layout")
        print(f"{'='*50}")
        print(f"{'':>10}SCREEN")
        print()
        
        for row_idx in range(self.rows):
            row_letter = chr(65 + row_idx)
            row_seats = sorted([s for s in self.seats.values() if s.row == row_letter], key=lambda x: x.number)
            
            line = f"  {row_letter}  "
            for seat in row_seats:
                if seat.is_reserved:
                    line += "[X] "
                elif seat.price_category == "VIP":
                    line += "[V] "
                else:
                    line += "[ ] "
            print(line)
        
        print(f"\n  [ ] = Available  [V] = VIP  [X] = Reserved")
        print(f"{'='*50}\n")

# ---

class Showtime:
    def __init__(self, showtime_id, movie, theater, start_time, base_price):
        self.showtime_id = showtime_id
        self.movie = movie      
        self.theater = theater  
        self.start_time = start_time 
        self.base_price = base_price
        self.reservations = []

    def get_available_seats(self):
        """Get available seats for this showtime"""
        reserved_ids = set()
        for res in self.reservations:
            reserved_ids.update([s.seat_id for s in res.reserved_seats])
        return [s for s in self.theater.seats.values() if s.seat_id not in reserved_ids]

    def suggest_best_seats(self, num_seats):
        """Suggest seats closest to center"""
        available = self.get_available_seats()
        if len(available) < num_seats:
            return None
        
        center_row = self.theater.rows // 2
        center_seat = self.theater.seats_per_row // 2
        
        
        available.sort(key=lambda s: abs(ord(s.row) - ord('A') - center_row) + abs(s.number - center_seat))
        return available[:num_seats]

# ---

class Reservation:
    def __init__(self, reservation_id, showtime, reserved_seats, customer_name):
        self.reservation_id = reservation_id
        self.showtime = showtime  
        self.reserved_seats = reserved_seats 
        self.customer_name = customer_name
        self.total_cost = 0.0
        self.is_cancelled = False

    def calculate_cost(self, price_per_category=None, discount=0):
        """Calculate price with category multipliers and discount"""
        if price_per_category is None:
            price_per_category = {'Standard': 1.0, 'VIP': 1.5}
        
        total = sum(self.showtime.base_price * price_per_category.get(s.price_category, 1.0) 
                   for s in self.reserved_seats)
        self.total_cost = total * (1 - discount / 100)
        return self.total_cost

    def cancel(self):
        """Cancel reservation"""
        if not self.is_cancelled:
            for seat in self.reserved_seats:
                seat.is_reserved = False
            self.is_cancelled = True
            return True
        return False

# ---

class CinemaSystem:
    """Main system manager"""
    def __init__(self):
        self.movies = {}
        self.theaters = {}
        self.showtimes = {}
        self.reservations = {}
        self.next_reservation_id = 1

    def add_movie(self, movie):
        self.movies[movie.movie_id] = movie

    def add_theater(self, theater):
        self.theaters[theater.theater_id] = theater

    def add_showtime(self, showtime):
        self.showtimes[showtime.showtime_id] = showtime

    def create_reservation(self, showtime_id, seat_ids, customer_name, discount=0):
        """Create new reservation"""
        if showtime_id not in self.showtimes:
            return None, "Invalid showtime"
        
        showtime = self.showtimes[showtime_id]
        available_ids = [s.seat_id for s in showtime.get_available_seats()]
        
        
        for sid in seat_ids:
            if sid not in available_ids:
                return None, f"Seat {sid} not available"
        
        
        seats = [showtime.theater.seats[sid] for sid in seat_ids]
        reservation = Reservation(self.next_reservation_id, showtime, seats, customer_name)
        reservation.calculate_cost(discount=discount)
        
        
        for seat in seats:
            seat.is_reserved = True
        
        showtime.reservations.append(reservation)
        self.reservations[self.next_reservation_id] = reservation
        self.next_reservation_id += 1
        
        return reservation, "Success"

    def cancel_reservation(self, reservation_id):
        """Cancel reservation"""
        if reservation_id not in self.reservations:
            return False, "Reservation not found"
        
        if self.reservations[reservation_id].cancel():
            return True, "Reservation cancelled"
        return False, "Already cancelled"

    def recommend_similar_movies(self, movie_id):
        """Recommend similar movies (genre and actor based)"""
        if movie_id not in self.movies:
            return []
        
        source = self.movies[movie_id]
        recommendations = []
        
        for movie in self.movies.values():
            if movie.movie_id == movie_id:
                continue
            
            score = 0
            if movie.genre == source.genre:
                score += 3
            common_actors = set(movie.actors) & set(source.actors)
            score += len(common_actors) * 2
            
            if score > 0:
                recommendations.append((movie, score))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in recommendations[:5]]

    def calculate_revenue(self):
        """Revenue analytics"""
        total = sum(r.total_cost for r in self.reservations.values() if not r.is_cancelled)
        count = sum(1 for r in self.reservations.values() if not r.is_cancelled)
        return {
            'total_revenue': total,
            'reservation_count': count,
            'avg_ticket_price': total / count if count > 0 else 0
        }


# ===== DEMO USAGE =====
if __name__ == "__main__":
    cinema = CinemaSystem()
    
    # Add movies
    movie1 = Movie(1, "Inception", 148, 8.8, "Sci-Fi", ["DiCaprio", "Hardy"])
    movie2 = Movie(2, "The Matrix", 136, 8.7, "Sci-Fi", ["Reeves", "Moss"])
    cinema.add_movie(movie1)
    cinema.add_movie(movie2)
    
    # Add theaters
    theater1 = Theater(1, "Theater 1", rows=8, seats_per_row=10)
    cinema.add_theater(theater1)
    
    # Add showtimes
    now = datetime.now()
    showtime1 = Showtime(1, movie1, theater1, now + timedelta(hours=2), 50.0)
    cinema.add_showtime(showtime1)
    
    # Show seat map
    theater1.render_seat_map()
    
    # Suggest best seats
    print(" Best 3 seat suggestions:")
    best_seats = showtime1.suggest_best_seats(3)
    for seat in best_seats:
        print(f"  - {seat.row}{seat.number} ({seat.price_category})")
    
    # Make reservation
    print("\n Creating reservation...")
    reservation, msg = cinema.create_reservation(1, [35, 36, 37], "John Doe", discount=10)
    if reservation:
        print(f" Success! Total: ${reservation.total_cost:.2f}")
    
    # Updated seat map
    theater1.render_seat_map()
    
    # Movie recommendations
    print("\n Similar to Inception:")
    similar = cinema.recommend_similar_movies(1)
    for movie in similar:
        print(f"  - {movie.title} ({movie.genre})")
    
    # Revenue report
    print("\n Revenue Report:")
    revenue = cinema.calculate_revenue()
    print(f"  Total Revenue: ${revenue['total_revenue']:.2f}")
    print(f"  Reservations: {revenue['reservation_count']}")
    print(f"  Average Ticket: ${revenue['avg_ticket_price']:.2f}")