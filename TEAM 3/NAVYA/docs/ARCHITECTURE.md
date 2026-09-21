\# System Architecture



\## BMW Enterprise Batch ETL Platform



\## 1. Architecture Overview



The BMW Enterprise Batch ETL Platform is designed as a batch-oriented data processing and analytics platform.



The system follows this high-level flow:



```text

BMW CSV Datasets

&#x20;      |

&#x20;      v

&#x20;  AWS S3 Raw

&#x20;      |

&#x20;      v

&#x20;PySpark ETL Pipeline

&#x20;      |

&#x20;      +--------------------+

&#x20;      |                    |

&#x20;      v                    v

Data Quality          Rejected Records

Validation                 |

&#x20;      |                    v

&#x20;      v               S3 Rejected

Processed Parquet

&#x20;      |

&#x20;      v

&#x20;  AWS S3 Processed

&#x20;      |

&#x20;      v

&#x20;AWS Glue Data Catalog

&#x20;      |

&#x20;      v

&#x20;  Amazon Athena

&#x20;      |

&#x20;      +----------------------+

&#x20;      |                      |

&#x20;      v                      v

&#x20;   FastAPI              SQL Analytics

&#x20;      |

&#x20;      v

&#x20;React Dashboard

&#x20;      |

&#x20;      v

&#x20;     User

