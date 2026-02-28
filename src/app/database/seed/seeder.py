from sqlalchemy.orm import Session
from .clear import clear_all_data
from .role import RoleSeeder
from .user import UserSeeder
from .room import RoomSeeder
from .tenant import TenantSeeder
from .invoice import InvoiceSeeder
from .payment import PaymentSeeder
from ...utils.color import Colors

class DatabaseSeeder:
    """Main orchestrator for seeding database"""
    
    def __init__(self, db: Session):
        self.db = db
        self.results = {}

    def run(self, num_tenants: int = 20, num_rooms: int = 20, clear_first: bool = True):
        """Execute full seeding workflow"""
        Colors.print("🌱 Starting database seeding...", Colors.HEADER)
        
        # Step 0: Clear existing data
        if clear_first:
            clear_all_data(self.db)
        
        # Step 1: Seed Roles
        Colors.info("Seeding roles...")
        roles = RoleSeeder(self.db).seed()
        self.results["roles"] = roles
        
        # Step 2: Seed Users
        Colors.info("Seeding users...")
        user_seeder = UserSeeder(self.db)
        user_seeder.seed_admin(roles["admin"].id)
        user_seeder.seed_staff(roles["staff"].id)
        
        # Step 3: Seed Rooms
        Colors.info("Seeding rooms...")
        rooms = RoomSeeder(self.db, count=num_rooms).seed()
        self.results["rooms"] = rooms
        
        # Step 4: Seed Tenants (only for occupied rooms)
        Colors.info("Seeding tenants...")
        occupied = [r for r in rooms if not r.is_available]
        tenants = TenantSeeder(self.db, count=num_tenants).seed(occupied)
        self.results["tenants"] = tenants
        
        # Step 5: Seed Invoices
        Colors.info("Seeding invoices...")
        invoices = InvoiceSeeder(self.db).seed(tenants)
        self.results["invoices"] = invoices
        
        # Step 6: Seed Payments
        Colors.info("Seeding payments...")
        payments = PaymentSeeder(self.db).seed(invoices)
        self.results["payments"] = payments
        
        # Final commit
        self.db.commit()
        
        # Print summary
        self._print_summary()
        return self.results

    def _print_summary(self):
        """Print seeding summary"""
        from src.app.model.role import Role
        from src.app.model.user import User
        from src.app.model.room import Room
        from src.app.model.tenant import Tenant
        from src.app.model.invoice import Invoice, InvoiceStatus
        from src.app.model.payment import Payment
        
        Colors.print("\n✅ Seeding completed!", Colors.OKGREEN)
        Colors.print("\n📊 Database Summary:", Colors.BOLD)
        print(f"   Roles:     {self.db.query(Role).count()}")
        print(f"   Users:     {self.db.query(User).count()}")
        print(f"   Rooms:     {self.db.query(Room).count()}")
        print(f"   Tenants:   {self.db.query(Tenant).filter(Tenant.is_active == True).count()} (active)")
        print(f"   Invoices:  {self.db.query(Invoice).count()}")
        print(f"   Payments:  {self.db.query(Payment).count()}")
        
        # Invoice breakdown
        paid = self.db.query(Invoice).filter(Invoice.status == InvoiceStatus.paid).count()
        late = self.db.query(Invoice).filter(Invoice.status == InvoiceStatus.late).count()
        pending = self.db.query(Invoice).filter(Invoice.status == InvoiceStatus.pending).count()
        
        Colors.print(f"\n💰 Invoice Status:", Colors.BOLD)
        print(f"   Paid:    {paid} {Colors.OKGREEN}✓{Colors.ENDC}")
        print(f"   Late:    {late} {Colors.WARNING}⚠{Colors.ENDC}")
        print(f"   Pending: {pending} {Colors.OKBLUE}●{Colors.ENDC}")