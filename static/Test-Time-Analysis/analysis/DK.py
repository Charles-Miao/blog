
# coding: utf-8

# In[8]:


import pandas as pd
RelativeTestTime=pd.Series([0.889250814,1.022801303,1.029315961,1.056677524])
MemoryScore=pd.Series([7.8,5.9,5.9,5.5])
CpuScore=pd.Series([7.8,7.2,7.2,7.2])
DiskScore=pd.Series([5.9,5.9,5.9,5.9])
CPUTemperature=pd.Series([44.1,56.5,84.1,79.5])
CPULoading=pd.Series([7,46.4,72,60.8])
MemoryAvailable=pd.Series([5.89,2.28,1.21,0.45])


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

