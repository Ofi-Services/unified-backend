from django.core.management.base import BaseCommand
import time 
import csv
import os
from django.conf import settings
from rapidfuzz import fuzz
from rapidfuzz.distance import DamerauLevenshtein, JaroWinkler
import csv
from api.models import Invoice
from django.utils.dateparse import parse_datetime
from django.conf import settings
import os
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):

    invoice1 = {
                    "reference": "Inv-241",
                    "date": "4/1/2025",
                    "value": '17281.43596',
                    "vendor": "Acme Corporation",
                    "region": "East",
                    "description": "Accounting Services",
                    "payment_method": "Bank Transfer",
                    "special_instructions": "Payment due within 30 days of invoice date"
                    }
        
    invoice2 = {
            "reference": "Inv-3125",
            "date": "2/13/2025",
            "value": '1200',
            "vendor": "Manhattan Corp.",
            "region": "West",
            "description": "Licensing Fees",
            "payment_method": "Credit Card",
            "special_instructions": ""
            }
        
    invoice3 = {
            "reference": "Inv-801",
            "date": "13/2025",
            "value": '16408.82687',
            "vendor": "Pyramid Systems",
            "region": "North",
            "description": "Community Outreach Programs",
            "payment_method": "PayPal",
            "special_instructions": ""
            }
     
    def normalize(self, s):
        return s.replace(' ', '').replace('-', '').replace('/', '').replace('.', '').lower()

    # Calculates the Damerau Levenshtein distance between two strings. Useful for common typos in long strings.
    def dl_distance(self, s1, s2):
        return DamerauLevenshtein.normalized_similarity(self.normalize(s1), self.normalize(s2))

    # Calculates the Jaro Winkler distance between two strings. Useful for common typos in short strings.
    def jaro_winkler_distance(self, s1, s2):
        return JaroWinkler.normalized_similarity(self.normalize(s1), self.normalize(s2))
    
    def jaccard_similarity(self, s1, s2):
        s1 = set(self.normalize(s1))
        s2 = set(self.normalize(s2))
        return len(s1.intersection(s2)) / len(s1.union(s2))
    
    def indel_distance(self, s1, s2):
        return fuzz.ratio(self.normalize(s1), self.normalize(s2))/100
    
    def compare_metrics(self, s1, s2):
        start_time = time.time()
        print(self.indel_distance(s1,s2), 'indel distance took ', time.time()-start_time, ' seconds')

        start_time = time.time()
        print(self.dl_distance(s1, s2), 'Damerau Levenshtein distance took ', time.time()-start_time, ' seconds')

        start_time = time.time()
        print(self.jaro_winkler_distance(s1, s2), 'Jaro Winkler distance took ', time.time()-start_time, ' seconds')

        start_time = time.time()
        print(self.jaccard_similarity(s1, s2), 'Jaccard similarity took ', time.time()-start_time, ' seconds')
    
    def stringify(self, dict):
        return ' '.join([self.normalize(str(dict[key])) for key in dict])
    
    def similarity(self, similarity):

        if similarity == 1:
            return 'EXACT'
        elif similarity > 0.95:
            return 'HIGH'
        elif similarity > 0.9:
            return 'MEDIUM'
        elif similarity > 0.8:
            return 'LOW'
        else:
            return 'NONE'
    
    def find_accuracies(self, d1, d2):
        accuracy_dict = {}
        for key in d1: 
            accuracy_dl = self.dl_distance(d1[key], d2[key])
            accuracy_jw = self.jaro_winkler_distance(d1[key], d2[key])
            accuracy_dict[key] = max(accuracy_dl, accuracy_jw)
        return accuracy_dict
    
    def find_patterns(self, dic):
        patterns = []
        for key in dic:
            if dic[key] > 0.9 and dic[key] < 1:
                patterns.append('similar ' + key)
        return patterns

    def test_invoices(self, invoice1, invoice2):
       
        


        str1 = self.stringify(invoice1)
        str2 = self.stringify(invoice2)

        similarity = self.indel_distance(str1, str2)
        print('similarity: ', similarity,' ', self.similarity(similarity))

        accuracies = self.find_accuracies(invoice1, invoice2)
        print(accuracies)
        patterns = self.find_patterns(accuracies)
        print(patterns)

    
    def get_data(self):
                # Path to the input CSV file
        input_csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'OutputData.csv')
        
       

        # Read data from the input CSV file
        with open(input_csv_file_path, newline='', encoding='utf-8-sig') as input_csvfile:
            reader = csv.DictReader(input_csvfile)
            data = [row for row in reader]
        return data
    
    def get_invoice(self, row):
        return {
            "reference": row['reference'],
            "date": row['Date'],
            "value": row['value'],
            "vendor": row['Vendor'],
            "region": row['Region'],
            "description": row['Description'],
            "payment_method": row['Payment Method'],
            "special_instructions": row['Special Intructions']
        }
    
    def find_most_similar(self, invoice):
        data = self.get_data()
        similarities = []
        for row in data:
            invoice1 = self.get_invoice(row)
            str1 = self.stringify(invoice)
            str2 = self.stringify(invoice1)
            similarity = self.indel_distance(str1, str2)
            similarities.append((similarity, row))
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[0]

    def find_most_similar_data(self, invoice):
        most_similar = self.get_invoice(self.find_most_similar(invoice)[1])
        print('Most similar invoice: ', most_similar['reference'])
        self.test_invoices(invoice, most_similar)

    def similar_text(self, text):
        """
        Return a similar text based on the input text.
        """
        case = random.choice([0, 1, 2])
        if case == 0:
            return self.delete_random_char(text)
        elif case == 1:
            return self.duplicate_random_char(text)
        else:
            return self.replace_random_char(text)


    def delete_random_char(self, text):
        """
        Delete a random character from the input text.
        """
        if len(text) > 0:
            index = random.randint(0, len(text) - 1)
            return text[:index] + text[index + 1:]
        return text
    
    def duplicate_random_char(self, text):
        """
        Duplicate a random character from the input text.
        """
        if len(text) > 0:
            index = random.randint(0, len(text) - 1)
            return text[:index] + text[index] + text[index:]
        return text
    
    def replace_random_char(self, text):
        """
        Replace a random character from the input text.
        """
        if len(text) > 0:
            index = random.randint(0, len(text) - 1)
            return text[:index] + chr(random.randint(97, 122)) + text[index + 1:]
        return text
    
    def get_accuracy(self, confidence, pattern):
        """
        Get the accuracy based on the confidence level.
        """
        if pattern == 'Exact Match':
            return 100
        elif confidence == 'High':
            return random.randint(95, 99)
        elif confidence == 'Medium':
            return random.randint(90, 94)
        elif confidence == 'Low':
            return random.randint(80, 89)
        else:
            return random.randint(0, 49)
        

    def create_invoices(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """
        # Path to the CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'DummyData.csv')

        # Read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            counter = 0

            for row in reader:
                duplicate_n = random.randint(1, 5)
                invoice_ref = 'INV-' + str(counter)
                date_str = row['Earliest Due Date']
                if date_str == '':
                    date = datetime(2025, 1, 1) + timedelta(days=counter + random.randint(1, 100))
                else:
                    try:
                        date = datetime.strptime(date_str, '%m/%d/%Y')
                    except ValueError:
                        raise ValueError(f"Invalid date format: {date_str} in row {counter}")
                quantity = random.randint(1, 12)
                value = Decimal(row['Group Value'])
                unit_price = value / quantity
                vendor = row['Vendor'].split(' - ', 1)[-1]
                pattern = row['Group Pattern']
                open_ = random.choice([True, False])
                group_id = row['Group UUID']
                confidence = row['Confidence'].strip()
                region = random.choice(['North', 'South', 'East', 'West'])
                description = row['Description']
                payment_method = random.choice(['Credit Card', 'Bank Transfer', 'PayPal', 'Cash'])
            
                pay_date = date + timedelta(days=random.randint(15, 30)) if random.choice([True, False]) else None
                special_instructions = row['Special Intructions']
                accuracy = self.get_accuracy(confidence, pattern)
            
                if 'Open' in row['Group Contains']:
                    open_ = True
                else:
                    open_ = False
            
                Invoice.objects.create(
                    reference=invoice_ref,
                    date=date,
                    quantity=quantity,
                    unit_price=unit_price,
                    value=value,
                    vendor=vendor,
                    pattern=pattern,
                    open=open_,
                    group_id=group_id,
                    confidence=confidence,
                    region=region,
                    description=description,
                    payment_method=payment_method,
                    pay_date=pay_date,
                    special_instructions=special_instructions,
                    accuracy=accuracy
                )
            
                counter += 1
            
                # Add duplicate data based on the pattern
                for i in range(0, duplicate_n):
                    invoice_ref = 'INV-' + str(counter)
                    if pattern == 'Similar Value':
                        value = str(float(value) + random.randint(-30, 30))
                    elif pattern == 'Similar Vendor':
                        vendor = self.similar_text(vendor)
                    elif pattern == 'Similar Date':
                        date = date + timedelta(days=i)
                    elif pattern == 'Similar Reference':
                        invoice_ref = self.similar_text(invoice_ref)
                    elif pattern == 'Similar Description':
                        description = self.similar_text(description)
                    counter += 1
            
                    Invoice.objects.create(
                        reference=invoice_ref,
                        date=date,
                        quantity=quantity,
                        unit_price=unit_price,
                        value=value,
                        vendor=vendor,
                        pattern=pattern,
                        open=open_,
                        group_id=group_id,
                        confidence=confidence,
                        region=region,
                        description=description,
                        payment_method=payment_method,
                        pay_date=pay_date,
                        special_instructions=special_instructions,
                        accuracy=accuracy
                    )
        self.stdout.write(self.style.SUCCESS('Data added successfully'))
    def handle(self, *args, **kwargs):
        """
        Handle the command to calculate the similarity between two invoices.
        """
        #self.find_most_similar_data(self.invoice3)
        # self.create_invoices()

