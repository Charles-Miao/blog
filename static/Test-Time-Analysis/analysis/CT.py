
# coding: utf-8

# In[1]:


import pandas as pd
RelativeTestTime=pd.Series([0.977777778,0.978571429,0.98968254,1.01031746,1.012698413,1.033333333])
MemoryScore=pd.Series([7.5,5.5,5.5,5.9,5.9,7.6])
CpuScore=pd.Series([6.9,7,7.1,6.9,6.8,7.2])
DiskScore=pd.Series([5.9,0,5.9,5.9,5.6,5.9])
CPUTemperature=pd.Series([75.5,59.56,71.9,63.1,40.6,104.4])
CPULoading=pd.Series([18.8,10.9,35.2,55.8,21.9,60.7])
MemoryAvailable=pd.Series([5,1.6,1.1,1.95,1.72,5.13])


# In[36]:


RelativeTestTime.corr(MemoryScore)


# In[37]:


RelativeTestTime.corr(CpuScore)


# In[38]:


RelativeTestTime.corr(DiskScore)


# In[39]:


RelativeTestTime.corr(CPUTemperature)


# In[40]:


RelativeTestTime.corr(CPULoading)


# In[41]:


RelativeTestTime.corr(MemoryAvailable)


# In[42]:


MemoryScore.corr(MemoryAvailable)


# In[43]:


CpuScore.corr(CPUTemperature)


# In[44]:


CpuScore.corr(CPULoading)


# In[45]:


CPULoading.corr(CPUTemperature)

