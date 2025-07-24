import pandas as pd
import re
import os
import io
import tempfile
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from services.database_service import DatabaseService
from services.bank_statement_parser import BankStatementParser

class DocumentParserService:
    """Service for parsing financial documents"""
    
    SUPPORTED_FORMATS = ['.pdf', '.csv', '.xls', '.xlsx']
    
    @classmethod
    def parse_document(cls, file_obj: BinaryIO, filename: str, document_type: str = None) -> Tuple[List[Dict[str, Any]], str]:
        """
        Parse a financial document and extract transactions
        
        Args:
            file_obj: File object (binary)
            filename: Original filename
            document_type: Type of document (bank, credit, brokerage)
            
        Returns:
            Tuple of (transactions, detected_type)
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(filename.lower())
            
            if ext not in cls.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported file format: {ext}. Supported formats: {', '.join(cls.SUPPORTED_FORMATS)}")
            
            # If document type not provided, try to detect it
            detected_type = document_type or cls._detect_document_type(file_obj, filename, ext)
            
            # Parse based on document type and extension
            if ext == '.pdf':
                transactions = cls._parse_pdf(file_obj, detected_type)
            elif ext == '.csv':
                transactions = cls._parse_csv(file_obj, detected_type)
            elif ext in ['.xls', '.xlsx']:
                transactions = cls._parse_excel(file_obj, detected_type)
            else:
                transactions = []
            
            # Validate transactions
            if not transactions:
                raise ValueError(f"No transactions found in the {detected_type} statement. Please check the file format.")
            
            return transactions, detected_type
            
        except ValueError as e:
            raise ValueError(str(e))
        except pd.errors.EmptyDataError:
            raise ValueError("The file appears to be empty. Please check the file and try again.")
        except pd.errors.ParserError:
            raise ValueError("Unable to parse the file. The format may be incorrect or corrupted.")
        except Exception as e:
            raise Exception(f"Error parsing document: {str(e)}")
    
    @classmethod
    def _detect_document_type(cls, file_obj: BinaryIO, filename: str, ext: str) -> str:
        """
        Detect the type of financial document
        
        Returns:
            Document type: 'bank', 'credit', or 'brokerage'
        """
        # Simple detection based on filename
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['bank', 'checking', 'saving', 'deposit']):
            return 'bank'
        elif any(keyword in filename_lower for keyword in ['credit', 'card', 'visa', 'mastercard']):
            return 'credit'
        elif any(keyword in filename_lower for keyword in ['broker', 'invest', 'stock', 'etf', 'mutual', 'fund']):
            return 'brokerage'
        
        # Default to bank statement
        return 'bank'
    
    @classmethod
    def _parse_pdf(cls, file_obj: BinaryIO, document_type: str) -> List[Dict[str, Any]]:
        """Parse PDF document based on type"""
        # Check if PDF libraries are available
        pdf_support = cls._check_pdf_support()
        
        if not pdf_support:
            return [{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": "PDF parsing libraries not installed. Please install them from the Upload Documents page.",
                "amount": 0.0,
                "type": "Expense",
                "category": "Other",
                "payment_method": "Other"
            }]
        
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                file_obj.seek(0)
                temp_file.write(file_obj.read())
                temp_path = temp_file.name
            
            try:
                transactions = []
                
                # Try pdfplumber first (best for text-based PDFs)
                try:
                    import pdfplumber
                    
                    with pdfplumber.open(temp_path) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                        
                        if text.strip() and document_type == 'bank':
                            # Use the dynamic bank statement parser
                            parsed_transactions, metadata = BankStatementParser.parse_text(text)
                            
                            # Add metadata to transactions
                            if metadata and parsed_transactions:
                                # DO NOT process statement metadata here - it will be done in document_upload_page.py
                                # after the account type is set
                                
                                for transaction in parsed_transactions:
                                    # Store metadata in additional_data for database storage
                                    if 'additional_data' not in transaction:
                                        transaction['additional_data'] = {}
                                    transaction['additional_data']['statement_metadata'] = metadata
                                    
                                    # Also keep it directly accessible for immediate use
                                    transaction['statement_metadata'] = metadata
                            
                            transactions.extend(parsed_transactions)
                except ImportError:
                    print("pdfplumber not available")
                except Exception as e:
                    print(f"Error extracting text with pdfplumber: {e}")
                
                # If no transactions found, try PyPDF2
                if not transactions:
                    try:
                        import PyPDF2
                        
                        with open(temp_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = ""
                            
                            for page_num in range(len(pdf_reader.pages)):
                                text += pdf_reader.pages[page_num].extract_text()
                            
                            if text.strip() and document_type == 'bank':
                                # Use the dynamic bank statement parser
                                parsed_transactions, metadata = BankStatementParser.parse_text(text)
                                
                                # Add metadata to transactions
                                if metadata and parsed_transactions:
                                    # DO NOT process statement metadata here - it will be done in document_upload_page.py
                                    # after the account type is set
                                    
                                    for transaction in parsed_transactions:
                                        # Store metadata in additional_data for database storage
                                        if 'additional_data' not in transaction:
                                            transaction['additional_data'] = {}
                                        transaction['additional_data']['statement_metadata'] = metadata
                                        
                                        # Also keep it directly accessible for immediate use
                                        transaction['statement_metadata'] = metadata
                                
                                transactions.extend(parsed_transactions)
                    except ImportError:
                        print("PyPDF2 not available")
                    except Exception as e:
                        print(f"Error extracting text with PyPDF2: {e}")
                
                # If still no transactions, try tabula for tables
                if not transactions:
                    try:
                        import tabula
                        
                        tables = tabula.read_pdf(temp_path, pages='all', multiple_tables=True)
                        if tables:
                            for df in tables:
                                if not df.empty:
                                    if document_type == 'bank':
                                        transactions.extend(cls._parse_bank_statement_df(df))
                    except ImportError:
                        print("tabula-py not available")
                    except Exception as e:
                        print(f"Error extracting tables with tabula: {e}")
                
                # If no transactions found, create a placeholder
                if not transactions:
                    raise ValueError("Could not extract any transactions from the PDF. The file may be scanned or in an unsupported format.")
                
                return transactions
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    @classmethod
    def _parse_csv(cls, file_obj: BinaryIO, document_type: str) -> List[Dict[str, Any]]:
        """Parse CSV document based on type"""
        try:
            # Reset file pointer
            file_obj.seek(0)
            
            # Read CSV
            df = pd.read_csv(file_obj)
            
            if df.empty:
                raise ValueError("No data found in the CSV file.")
            
            # Parse based on document type
            if document_type == 'bank':
                return cls._parse_bank_statement_df(df)
            elif document_type == 'credit':
                return cls._parse_credit_statement_df(df)
            elif document_type == 'brokerage':
                return cls._parse_brokerage_statement_df(df)
            else:
                return []
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    @classmethod
    def _parse_excel(cls, file_obj: BinaryIO, document_type: str) -> List[Dict[str, Any]]:
        """Parse Excel document based on type"""
        try:
            # Reset file pointer
            file_obj.seek(0)
            
            # Read Excel
            df = pd.read_excel(file_obj)
            
            if df.empty:
                raise ValueError("No data found in the Excel file.")
            
            # Parse based on document type
            if document_type == 'bank':
                return cls._parse_bank_statement_df(df)
            elif document_type == 'credit':
                return cls._parse_credit_statement_df(df)
            elif document_type == 'brokerage':
                return cls._parse_brokerage_statement_df(df)
            else:
                return []
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"Error parsing Excel file: {str(e)}")
    
    @classmethod
    def _parse_bank_statement_df(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse bank statement DataFrame"""
        transactions = []
        
        try:
            # Try to identify columns
            date_col = cls._find_column(df, ['date', 'transaction date', 'posted date'])
            desc_col = cls._find_column(df, ['description', 'transaction', 'details', 'memo'])
            amount_col = cls._find_column(df, ['amount', 'transaction amount'])
            
            if not all([date_col, desc_col, amount_col]):
                # Use fallback for Bank of America statements
                if len(df.columns) >= 2:
                    # Try to use the first column as date and last column as amount
                    date_col = df.columns[0]
                    amount_col = df.columns[-1]
                    
                    # If there are at least 3 columns, use the middle one as description
                    if len(df.columns) >= 3:
                        desc_col = df.columns[1]
                    else:
                        # Create a placeholder description
                        df['Description'] = "Bank transaction"
                        desc_col = 'Description'
                else:
                    raise ValueError("Could not identify required columns in the bank statement. Please check the file format.")
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_val = row[date_col]
                    if isinstance(date_val, str):
                        # Try common date formats
                        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y']:
                            try:
                                date_obj = datetime.strptime(date_val, fmt)
                                break
                            except ValueError:
                                continue
                    else:
                        # Assume pandas datetime
                        date_obj = date_val
                    
                    date = date_obj.strftime('%Y-%m-%d')
                    
                    # Parse description
                    description = str(row[desc_col]).strip()
                    
                    # Parse amount
                    amount = float(row[amount_col])
                    
                    # Determine transaction type
                    transaction_type = 'Income' if amount >= 0 else 'Expense'
                    amount = abs(amount)  # Make amount positive
                    
                    # Create transaction with standard fields
                    transaction = {
                        'date': date,
                        'description': description,
                        'amount': amount,
                        'type': transaction_type,
                        'category': 'Uncategorized',
                        'payment_method': 'Bank Transfer'
                    }
                    
                    # Add all other columns as additional data
                    for col in df.columns:
                        if col not in [date_col, desc_col, amount_col] and not pd.isna(row[col]):
                            # Convert any non-string values to string
                            transaction[f'original_{col}'] = str(row[col])
                    
                    transactions.append(transaction)
                except Exception as e:
                    print(f"Error parsing row: {e}")
            
            return transactions
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"Error parsing bank statement: {str(e)}")
    
    @classmethod
    def _parse_credit_statement_df(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse credit card statement DataFrame"""
        # Similar implementation to bank statement parsing
        return []
    
    @classmethod
    def _parse_brokerage_statement_df(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse brokerage statement DataFrame"""
        # Similar implementation to bank statement parsing
        return []
    
    @staticmethod
    def _find_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column in the DataFrame based on possible names"""
        for name in possible_names:
            # Check for exact match
            if name in df.columns:
                return name
            
            # Check for case-insensitive match
            for col in df.columns:
                if name.lower() == col.lower():
                    return col
            
            # Check for partial match
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        
        return None
    
    @staticmethod
    def _check_pdf_support() -> bool:
        """Check if PDF parsing libraries are installed"""
        try:
            import importlib.util
            
            # Check for pdfplumber (preferred)
            pdfplumber_spec = importlib.util.find_spec("pdfplumber")
            if pdfplumber_spec is not None:
                return True
            
            # Check for PyPDF2
            pypdf2_spec = importlib.util.find_spec("PyPDF2")
            if pypdf2_spec is None:
                return False
            
            return True
        except ImportError:
            return False
    
    @classmethod
    def save_transactions_to_db(cls, transactions: List[Dict[str, Any]]) -> int:
        """Save parsed transactions to the database"""
        count = 0
        errors = []
        
        try:
            for transaction in transactions:
                try:
                    # Validate transaction data
                    if 'date' not in transaction or not transaction['date']:
                        errors.append(f"Missing date in transaction: {transaction}")
                        continue
                        
                    if 'amount' not in transaction or not transaction['amount']:
                        errors.append(f"Missing amount in transaction: {transaction}")
                        continue
                        
                    if 'type' not in transaction or not transaction['type']:
                        errors.append(f"Missing type in transaction: {transaction}")
                        continue
                    
                    # Add transaction to database
                    DatabaseService.add_transaction(transaction)
                    count += 1
                except Exception as e:
                    errors.append(f"Error saving transaction: {str(e)}")
            
            # If there were errors but some transactions were saved
            if errors and count > 0:
                print(f"Saved {count} transactions with {len(errors)} errors: {errors}")
            # If there were only errors and no transactions saved
            elif errors and count == 0:
                error_msg = "\n".join(errors[:5])  # Show first 5 errors
                raise ValueError(f"Failed to save any transactions. Errors:\n{error_msg}")
            
            return count
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise Exception(f"Error saving transactions to database: {str(e)}")