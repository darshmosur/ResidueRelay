from typing import List, Tuple
from app.models.farm import Farm, Coordinates
from app.models.baler import Baler
from app.models.buyer import Buyer
from app.models.state import SimulationState

def seed_farms() -> List[Farm]:
    """15 realistic farms across Karnal/Kurukshetra agricultural belt."""
    raw_farms = [
        # Cluster 1: Taraori (Basmati Rice Belt)
        {
            "id": "farm-01",
            "farmer_name": "Gurpreet Singh",
            "phone": "+91 98120 44101",
            "village": "Taraori",
            "cluster": "Taraori",
            "lat": 29.805,
            "lng": 76.924,
            "acres": 8.0,
            "harvest_time_hours": 0.0,      # Ready right at T0
            "sowing_deadline_hours": 48.0,   # 2 days window
            "raw_text": "Mera 8 acre PR-126 kat gaya hai Taraori GT Road ke paas. Parso tak khet khali chahiye gehu ki buaayi ke liye.",
            "notes": "Large field with wide tractor access from GT road."
        },
        {
            "id": "farm-02",
            "farmer_name": "Rameshwar Dass",
            "phone": "+91 94160 33812",
            "village": "Taraori",
            "cluster": "Taraori",
            "lat": 29.812,
            "lng": 76.938,
            "acres": 5.5,
            "harvest_time_hours": 2.0,
            "sowing_deadline_hours": 52.0,
            "raw_text": "Rameshwar Taraori se, 5.5 acre dhaan ki straw padi hai. 2 din me clear karwa do bhai.",
            "notes": "Medium moisture, bunds leveled."
        },
        {
            "id": "farm-03",
            "farmer_name": "Harinder Gill",
            "phone": "+91 98961 88204",
            "village": "Nadana",
            "cluster": "Taraori",
            "lat": 29.792,
            "lng": 76.915,
            "acres": 11.0,
            "harvest_time_hours": 4.0,
            "sowing_deadline_hours": 55.0,
            "raw_text": "Nadana gaon, 11 kille dhaan cut chuka hai combine se. Stubble cutter chal gaya hai, baler bhej do jaldi.",
            "notes": "High yield 1109 variety, thick straw."
        },
        {
            "id": "farm-04",
            "farmer_name": "Balwinder Cheema",
            "phone": "+91 97280 11923",
            "village": "Sultanpur",
            "cluster": "Taraori",
            "lat": 29.821,
            "lng": 76.905,
            "acres": 6.0,
            "harvest_time_hours": 6.0,
            "sowing_deadline_hours": 58.0,
            "raw_text": "Sultanpur farm, 6 acre area ready for baling tomorrow morning.",
            "notes": "Single plot, dry straw."
        },
        
        # Cluster 2: Nilokheri (North Zone)
        {
            "id": "farm-05",
            "farmer_name": "Rajinder Verma",
            "phone": "+91 98132 55901",
            "village": "Nilokheri",
            "cluster": "Nilokheri",
            "lat": 29.835,
            "lng": 76.912,
            "acres": 7.5,
            "harvest_time_hours": 0.0,
            "sowing_deadline_hours": 46.0,
            "raw_text": "Nilokheri railway line ke paas 7.5 kille hain. Super seeder lagana hai parso.",
            "notes": "Adjacent to canal minor."
        },
        {
            "id": "farm-06",
            "farmer_name": "Jasbir Sandhu",
            "phone": "+91 94671 22845",
            "village": "Pujam",
            "cluster": "Nilokheri",
            "lat": 29.845,
            "lng": 76.930,
            "acres": 12.0,
            "harvest_time_hours": 8.0,
            "sowing_deadline_hours": 60.0,
            "raw_text": "Jasbir from Pujam village, 12 acre ready by afternoon. Tractor trolley route clear.",
            "notes": "High priority client, regular co-op member."
        },
        {
            "id": "farm-07",
            "farmer_name": "Kuldeep Mann",
            "phone": "+91 98965 33119",
            "village": "Samana Bahu",
            "cluster": "Nilokheri",
            "lat": 29.855,
            "lng": 76.945,
            "acres": 4.5,
            "harvest_time_hours": 12.0,
            "sowing_deadline_hours": 64.0,
            "raw_text": "Samana Bahu, 4.5 acre paddy straw lying in windrows.",
            "notes": "Small farmer, windrowed manually."
        },
        {
            "id": "farm-08",
            "farmer_name": "Manjit Dhillon",
            "phone": "+91 93550 77124",
            "village": "Anjanthali",
            "cluster": "Nilokheri",
            "lat": 29.838,
            "lng": 76.885,
            "acres": 9.0,
            "harvest_time_hours": 14.0,
            "sowing_deadline_hours": 68.0,
            "raw_text": "Anjanthali gaon, 9 acre field. Gehu ki bjaayi 3 din baad schedule hai.",
            "notes": "Good road access."
        },

        # Cluster 3: Indri (East Agricultural Belt)
        {
            "id": "farm-09",
            "farmer_name": "Sukhdev Brar",
            "phone": "+91 98122 88419",
            "village": "Indri",
            "cluster": "Indri",
            "lat": 29.882,
            "lng": 77.062,
            "acres": 14.0,
            "harvest_time_hours": 2.0,
            "sowing_deadline_hours": 50.0,
            "raw_text": "Indri road par 14 acre ka chak. Kal subah baler chahiye har haal me.",
            "notes": "Very large contiguous parcel. Bio-CNG plant nearby."
        },
        {
            "id": "farm-10",
            "farmer_name": "Joginder Pal",
            "phone": "+91 94165 99012",
            "village": "Bhadaur",
            "cluster": "Indri",
            "lat": 29.870,
            "lng": 77.045,
            "acres": 6.5,
            "harvest_time_hours": 10.0,
            "sowing_deadline_hours": 66.0,
            "raw_text": "Bhadaur me 6.5 acre straw ready. Please arrange machine.",
            "notes": "Clean dry residue."
        },
        {
            "id": "farm-11",
            "farmer_name": "Virender Choudhary",
            "phone": "+91 98960 44231",
            "village": "Khanpur",
            "cluster": "Indri",
            "lat": 29.895,
            "lng": 77.080,
            "acres": 8.0,
            "harvest_time_hours": 16.0,
            "sowing_deadline_hours": 72.0,
            "raw_text": "Khanpur gaon, 8 acre ready tomorrow. Bio plant is 4 km away.",
            "notes": "Near Western Yamuna Canal."
        },
        {
            "id": "farm-12",
            "farmer_name": "Amrik Singh",
            "phone": "+91 97291 66348",
            "village": "Ghir",
            "cluster": "Indri",
            "lat": 29.860,
            "lng": 77.030,
            "acres": 5.0,
            "harvest_time_hours": 20.0,
            "sowing_deadline_hours": 74.0,
            "raw_text": "Ghir gaon se Amrik, 5 kille parso dophar tak katenge.",
            "notes": "Moisture will be slightly high until noon."
        },

        # Cluster 4: Karnal Central / South Zone
        {
            "id": "farm-13",
            "farmer_name": "Dharampal Sharma",
            "phone": "+91 98124 11772",
            "village": "Uchana",
            "cluster": "Karnal Central",
            "lat": 29.725,
            "lng": 76.968,
            "acres": 7.0,
            "harvest_time_hours": 6.0,
            "sowing_deadline_hours": 56.0,
            "raw_text": "Uchana lake ke paas 7 acre. Straw uthaane ke liye baler book karna hai.",
            "notes": "Easy approach via highway bypass."
        },
        {
            "id": "farm-14",
            "farmer_name": "Surjit Kang",
            "phone": "+91 94660 77319",
            "village": "Kunjpura",
            "cluster": "Karnal Central",
            "lat": 29.712,
            "lng": 77.085,
            "acres": 10.0,
            "harvest_time_hours": 18.0,
            "sowing_deadline_hours": 75.0,
            "raw_text": "Kunjpura sainik school side, 10 acre harvested. Fast clearance needed.",
            "notes": "Sandy loam soil, clears quickly."
        },
        {
            "id": "farm-15",
            "farmer_name": "Ravinder Grewal",
            "phone": "+91 98967 55409",
            "village": "Gharaunda",
            "cluster": "Karnal Central",
            "lat": 29.542,
            "lng": 76.972,
            "acres": 6.0,
            "harvest_time_hours": 24.0,
            "sowing_deadline_hours": 80.0,
            "raw_text": "Gharaunda farm, 6 acre straw available day after tomorrow.",
            "notes": "Direct link to Panipat industrial corridor."
        }
    ]

    farms = []
    for f in raw_farms:
        straw_tons = round(f["acres"] * 2.25, 1)  # 2.25 tons/acre average for North Indian paddy
        farms.append(Farm(
            id=f["id"],
            farmer_name=f["farmer_name"],
            phone=f["phone"],
            village=f["village"],
            cluster=f["cluster"],
            location=Coordinates(lat=f["lat"], lng=f["lng"]),
            acres=f["acres"],
            estimated_straw_tons=straw_tons,
            harvest_time_hours=f["harvest_time_hours"],
            sowing_deadline_hours=f["sowing_deadline_hours"],
            moisture_pct=14.5,
            status="pending",
            raw_request_text=f["raw_text"],
            notes=f["notes"]
        ))
    return farms

def seed_balers() -> List[Baler]:
    """3 balers stationed at distinct depots across Karnal district."""
    return [
        Baler(
            id="baler-01",
            operator_name="Sukhwinder Sandhu",
            operator_phone="+91 98120 11223",
            baler_type="Square Baler (Heavy Duty)",
            throughput_acres_per_hour=2.5,
            depot_location=Coordinates(lat=29.835, lng=76.912),  # Nilokheri Depot
            operating_hours_daily=(7, 19),  # 07:00 to 19:00 (12 daylight hours/day)
            status="available",
            notes="Primary high-speed baler with GPS telemetry"
        ),
        Baler(
            id="baler-02",
            operator_name="Gurmeet Singh",
            operator_phone="+91 94160 22334",
            baler_type="Standard Square Baler",
            throughput_acres_per_hour=2.0,
            depot_location=Coordinates(lat=29.805, lng=76.924),  # Taraori Depot
            operating_hours_daily=(7, 19),
            status="available",
            notes="Local cooperative baler (Subject to breakdown simulation in demo)"
        ),
        Baler(
            id="baler-03",
            operator_name="Jasbir Gill",
            operator_phone="+91 98960 33445",
            baler_type="Round Baler (Agri-Max)",
            throughput_acres_per_hour=2.2,
            depot_location=Coordinates(lat=29.882, lng=77.062),  # Indri Depot
            operating_hours_daily=(7, 19),
            status="available",
            notes="Stationed at Indri East depot near biomass hub"
        )
    ]

def seed_buyers() -> List[Buyer]:
    """4 off-taker straw buyers with realistic daily intake quotas and locations."""
    return [
        Buyer(
            id="buyer-01",
            name="Indri Compressed Bio-Gas (CBG) Plant",
            buyer_type="bio_cng",
            location=Coordinates(lat=29.886, lng=77.068),
            daily_intake_capacity_tons=90.0,
            price_per_ton=2050.0,
            contact_person="R.K. Sharma (Plant Head)",
            notes="High demand for green bio-CNG conversion; prefers low moisture"
        ),
        Buyer(
            id="buyer-02",
            name="Panipat Biomass Thermal Power Station",
            buyer_type="power_plant",
            location=Coordinates(lat=29.535, lng=76.980),
            daily_intake_capacity_tons=150.0,
            price_per_ton=1850.0,
            contact_person="Er. Anoop Malik",
            notes="Highest daily capacity; co-fires paddy straw pellets with coal"
        ),
        Buyer(
            id="buyer-03",
            name="Karnal Kraft Paper Mill",
            buyer_type="paper_mill",
            location=Coordinates(lat=29.690, lng=76.995),
            daily_intake_capacity_tons=60.0,
            price_per_ton=1950.0,
            contact_person="Sunil Aggarwal",
            notes="Requires clean golden straw without weeds for packaging paper"
        ),
        Buyer(
            id="buyer-04",
            name="Kurukshetra Briquetting & Fodder Depot",
            buyer_type="fodder_hub",
            location=Coordinates(lat=29.860, lng=76.890),
            daily_intake_capacity_tons=45.0,
            price_per_ton=2150.0,
            contact_person="Praveen Kumar",
            notes="Premium price for dry fodder pellets shipped to Rajasthan gaushalas"
        )
    ]

def get_initial_state() -> SimulationState:
    """Returns fresh baseline simulation state with 15 farms, 3 balers, 4 buyers."""
    return SimulationState(
        scenario="initial",
        farms=seed_farms(),
        balers=seed_balers(),
        buyers=seed_buyers(),
        current_plan=None,
        previous_plan=None,
        active_disruptions=[]
    )
