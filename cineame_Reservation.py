from datetime import datetime

class Movie:

    def __init__(self, title, duration_minutes, rating):
        self.title = title  
        self.duration_minutes = duration_minutes  
        self.rating = rating  

    def __str__(self):
        return f"Film: {self.title} ({self.duration_minutes} dk), Derece: {self.rating}"

# ---

class Seat:
    
    def __init__(self, seat_id, row, number, price_category="Standard"):
        self.seat_id = seat_id 
        self.row = row          
        self.number = number    
        self.price_category = price_category 
        self.is_reserved = False 

    def __str__(self):
        status = "REZERVE" if self.is_reserved else "BOŞ"
        return f"Koltuk: {self.row}{self.number} ({self.price_category}), Durum: {status}"
        
# ---

class Theater:
    
    def __init__(self, theater_id, name, capacity):
        self.theater_id = theater_id
        self.name = name  
        self.capacity = capacity
        
        self.seats = {} 

    def add_seat(self, seat):
        
        self.seats[seat.seat_id] = seat

    def __str__(self):
        return f"Salon: {self.name}, Kapasite: {self.capacity}, Koltuk Sayısı: {len(self.seats)}"

# ---

class Showtime:
   
    def __init__(self, showtime_id, movie, theater, start_time, base_price):
        self.showtime_id = showtime_id
        self.movie = movie      
        self.theater = theater  
        self.start_time = start_time 
        self.base_price = base_price
        self.reservations = [] 

    def __str__(self):
        time_str = self.start_time.strftime("%d/%m %H:%M")
        return (f"Gösterim ID: {self.showtime_id}\n"
                f"  Film: {self.movie.title}\n"
                f"  Salon: {self.theater.name}\n"
                f"  Saat: {time_str}\n"
                f"  Temel Fiyat: {self.base_price:.2f} TL")

# ---

class Reservation:
    
    def __init__(self, reservation_id, showtime, reserved_seats, customer_name):
        self.reservation_id = reservation_id
        self.showtime = showtime  
        self.reserved_seats = reserved_seats 
        self.customer_name = customer_name
        self.total_cost = 0.0 

    def calculate_cost(self, price_per_category={'Standard': 1.0, 'VIP': 1.5}):
        total = 0
        base = self.showtime.base_price
        for seat in self.reserved_seats:
            multiplier = price_per_category.get(seat.price_category, 1.0)
            total += base * multiplier
        self.total_cost = total
        return self.total_cost

    def __str__(self):
        seat_list = ", ".join([f"{s.row}{s.number}" for s in self.reserved_seats])
        return (f"--- Rezervasyon ID: {self.reservation_id} ---\n"
                f"  Müşteri: {self.customer_name}\n"
                f"  Film: {self.showtime.movie.title} ({self.showtime.start_time.strftime('%H:%M')})\n"
                f"  Koltuklar: {seat_list}\n"
                f"  Toplam Ücret: {self.total_cost:.2f} TL")
    

class CinemaManager:
    def __init__(self):
        self.movies = []
        self.showtimes = []
        self.reservations = []

    
    def filter_movies(self, genre=None):
        """Filter movies by genre. If genre is None, return all movies."""
        if not genre:
            return self.movies
        return [m for m in self.movies if m.genre.lower() == genre.lower()]

    
    def display_seat_map(self, showtime):
        """print seat map for a given showtime."""
        print(f"\n--- {showtime.theater.name} seat map ---")
        
        sorted_seats = sorted(showtime.theater.seats.values(), key=lambda x: x.seat_id)
        
        for i, seat in enumerate(sorted_seats):
            symbol = "[X]" if seat.is_reserved else "[ ]"
            print(f"{seat.seat_id}:{symbol}", end="\t")
            if (i + 1) % 5 == 0: # Her 5 koltukta bir alt satıra geç
                print()
        print("-----------------------------------")

    
    def purchase_ticket(self, customer_name, showtime, seat_ids):
        selected_seats = []
        for s_id in seat_ids:
            seat = showtime.theater.seats.get(s_id)
            if seat and not seat.is_reserved:
                selected_seats.append(seat)
            else:
                print(f"Hata: {s_id} koltuğu dolu veya geçersiz!")
                return None

       
        res_id = len(self.reservations) + 1
        new_res = Reservation(res_id, showtime, selected_seats, customer_name)
        new_res.calculate_cost()
        
        
        for s in selected_seats: s.is_reserved = True
        
        self.reservations.append(new_res)
        print(f"Başarılı! Toplam Ücret: {new_res.total_cost} TL")
        return new_res

   
    def cancel_reservation(self, reservation_id):
        res = next((r for r in self.reservations if r.reservation_id == reservation_id), None)
        if res:
            for seat in res.reserved_seats:
                seat.is_reserved = False 
            self.reservations.remove(res)
            print(f"Rezervasyon {reservation_id} başarıyla iptal edildi.")
        else:
            print("Rezervasyon bulunamadı.")