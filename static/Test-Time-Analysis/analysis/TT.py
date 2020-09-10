
# coding: utf-8

# In[8]:


import pandas as pd
RelativeTestTime=pd.Series([0.926890756,0.934453782,0.985714286,1.004201681,1.088235294,1.117647059])
MemoryScore=pd.Series([5.9,5.9,5.9,5.9,7.1,5.9])
CpuScore=pd.Series([7.2,7.1,7.1,6.8,6.8,6.8])
DiskScore=pd.Series([5.9,5.9,5.9,5.9,5.9,5.9])
CPUTemperature=pd.Series([46.6,47.4,49,38.7,55.7,41.1])
CPULoading=pd.Series([10.2,10.9,9.8,14.6,20.1,17.3])
MemoryAvailable=pd.Series([1.85,2.14,2.04,2.14,3.78,1.97])


# In[9]:


RelativeTestTime.corr(MemoryScore)


# In[10]:


RelativeTestTime.corr(CpuScore)


# In[11]:


RelativeTestTime.corr(DiskScore)


# In[12]:


RelativeTestTime.corr(CPUTemperature)


# In[13]:


RelativeTestTime.corr(CPULoading)


# In[14]:


RelativeTestTime.corr(MemoryAvailable)


# In[15]:


MemoryScore.corr(MemoryAvailable)


# In[16]:


CpuScore.corr(CPUTemperature)


# In[17]:


CpuScore.corr(CPULoading)


# In[18]:


CPULoading.corr(CPUTemperature)

